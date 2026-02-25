from fastapi import APIRouter, HTTPException, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.schemas import ChatQuery, ChatResponse, Source
from app.models.sql_schemas import ChatSession, ChatMessage
from app.services.llm import llm_service
from app.core.guardrails import guardrails
from app.core.database import get_session
from app.api.deps import get_current_active_user
from app.models.sql_schemas import User
from langchain_core.messages import HumanMessage, AIMessage
import json
import re

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

MAX_HISTORY_MESSAGES = 20  # Limit to avoid token overflow


async def _load_chat_history(db: AsyncSession, session_id: str) -> list:
    """Load previous messages from DB and convert to LangChain format."""
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()

    # Take only the last N messages to avoid token overflow
    messages = messages[-MAX_HISTORY_MESSAGES:]

    chat_history = []
    for msg in messages:
        if msg.role == "user":
            chat_history.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            chat_history.append(AIMessage(content=msg.content))

    return chat_history


async def _get_or_create_session(
    db: AsyncSession, session_id: str | None, user_id: int, title: str
) -> ChatSession:
    """Retrieve existing session or create a new one."""
    if session_id:
        stmt = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        if session:
            return session
        # If session_id was provided but not found, fall through to create new

    # Create new session
    session = ChatSession(title=title[:50], user_id=user_id)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("5/minute")
async def chat(
    request: Request,
    query: ChatQuery,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    try:
        # 1. Input Guardrail: Sanitize
        clean_query = guardrails.sanitize_input(query.query)

        # 2. Get or create session
        session = await _get_or_create_session(
            db, query.session_id, current_user.id, clean_query
        )

        # 3. Load chat history from DB (empty list if new session)
        chat_history = await _load_chat_history(db, session.id)

        # 4. Agent Logic — pass real chat history (with retry for Groq tool calling issues)
        rag_chain = llm_service.get_rag_chain()
        max_retries = 3
        response = None
        last_error = None

        for attempt in range(max_retries):
            try:
                response = rag_chain.invoke({
                    "input": clean_query,
                    "chat_history": chat_history,
                })
                break  # Success, exit retry loop
            except Exception as agent_err:
                last_error = agent_err
                print(f"⚠️ Agent attempt {attempt + 1}/{max_retries} failed: {agent_err}")
                if attempt < max_retries - 1:
                    import asyncio
                    await asyncio.sleep(1)  # Brief pause before retry

        if response is None:
            raise Exception(f"Agent failed after {max_retries} attempts: {last_error}")

        answer = response.get("output", "No answer generated.")
        sources = []

        # Extract citations from answer text using Regex
        # New format: [File - Página X] plus legacy formats
        citation_patterns = [
            r"\[(.*?)\s*-\s*Página\s*(\d+)\]",       # [File - Página X] (new primary)
            r"\[(.*?)\s*-\s*Pág\.?\s*(\d+)\]",       # [File - Pág. X]
            r"\[(.*?),\s*Pág\.?\s*(\d+)\]",           # [File, Pág. X] (legacy)
            r"\[(.*?),\s*Página\.?\s*(\d+)\]",        # [File, Página X] (legacy)
            r"\[(.*?\.pdf),\s*(\d+)\]",               # [File.pdf, X] (legacy)
        ]

        seen = set()
        for pattern in citation_patterns:
            matches = re.findall(pattern, answer)
            for filename, page_num in matches:
                key = (filename.strip(), int(page_num))
                if key not in seen:
                    seen.add(key)
                    sources.append(Source(
                        document_name=filename.strip(),
                        page_number=int(page_num),
                        content_snippet="Cited by Agent",
                        relevance_score=1.0,
                    ))

        chat_response = ChatResponse(
            answer=answer,
            sources=sources,
            session_id=session.id,
        )

        # 5. Output Guardrail: Hallucination Check
        is_valid, reason = guardrails.validate_response(chat_response)
        if not is_valid:
            print(f"GUARDRAIL ALERT: {reason}")
            answer += f"\n\n[ADVERTENCIA DEL SISTEMA: {reason}]"
            chat_response.answer = answer

        # 6. Persist messages
        user_msg = ChatMessage(
            session_id=session.id, role="user", content=clean_query
        )
        ai_msg = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=answer,
            sources=json.dumps([s.dict() for s in sources]),
        )
        db.add(user_msg)
        db.add(ai_msg)
        await db.commit()

        return chat_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

