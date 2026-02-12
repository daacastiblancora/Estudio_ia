from fastapi import APIRouter, HTTPException, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import ChatQuery, ChatResponse, Source
from app.models.sql_schemas import ChatSession, ChatMessage
from app.services.llm import llm_service
from app.core.guardrails import guardrails
from app.core.database import get_session
from app.api.deps import get_current_active_user
from app.models.sql_schemas import User
import json

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("5/minute") # Rate Limit: 5 requests per minute per IP
async def chat(
    request: Request, 
    query: ChatQuery,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    try:
        # 1. Input Guardrail: Sanitize
        clean_query = guardrails.sanitize_input(query.query)
        
        # 2. Get/Create Session (Simple implementation: create new if no ID, else retrieve)
        # For this MVP, we create a new session if not provided, or continue if client sends ID.
        # Ideally, this should come from the request headers or body.
        # Let's assume the client sends a session_id in the query object (we need to update schema)
        # or we just log it as a new message in a "default" session for now.
        
        # 3. Agent Logic
        # AgentExecutor expects 'input' and returns 'output'
        # History handling would be here in 'chat_history' if we implemented full conversation buffer
        rag_chain = llm_service.get_rag_chain()
        response = rag_chain.invoke({"input": clean_query, "chat_history": []})
        
        answer = response.get("output", "No answer generated.")
        sources = []
        
        # Agent might not return 'context' directly unless we customize the callback or return intermediate steps.
        # For now, we will parse sources from the text if present, or rely on the agent's citation.
        # Alternatively, we could fetch 'intermediate_steps' to see what the retriever tool returned.
        
        # NOTE: With Agents, source extraction is trickier.
        # We will check if 'intermediate_steps' exists and parse documents from there.
        if "intermediate_steps" in response:
            for action, observation in response["intermediate_steps"]:
                if action.tool == "search_internal_documents":
                    # Observation is likely a list of Documents or a string depending on the tool definition
                    # The create_retriever_tool usually returns a string, but let's see.
                    # Actually, create_retriever_tool returns a string of concatenated docs.
                    # We might want to pass the raw docs? 
                    # For MVP Agent, we might lose granular source metadata in the response object unless we modify the tool.
                    pass

        # Fallback: Extract citations from answer text using Regex if needed, or leave sources empty 
        # as the answer itself contains the citations per prompt.

        chat_response = ChatResponse(answer=answer, sources=sources)

        # 4. Output Guardrail: Hallucination Check
        is_valid, reason = guardrails.validate_response(chat_response)
        if not is_valid:
            print(f"GUARDRAIL ALERT: {reason}")
            answer += f"\n\n[ADVERTENCIA DEL SISTEMA: {reason}]"
            chat_response.answer = answer

        # 5. Persist Chat History (Async)
        # Create a session for this interaction (or use existing)
        session = ChatSession(title=clean_query[:30], user_id=current_user.id)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        # Log User Message
        user_msg = ChatMessage(session_id=session.id, role="user", content=clean_query)
        db.add(user_msg)
        
        # Log AI Message
        ai_msg = ChatMessage(
            session_id=session.id, 
            role="assistant", 
            content=answer, 
            sources=json.dumps([s.dict() for s in sources])
        )
        db.add(ai_msg)
        
        await db.commit()
        
        # Return session_id so frontend can continue (future)
        # chat_response.session_id = session.id 

        return chat_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
