from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.models.schemas import ChatQuery, ChatResponse, Source
from app.services.llm import llm_service
from app.core.guardrails import guardrails

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("5/minute") # Rate Limit: 5 requests per minute per IP
async def chat(request: Request, query: ChatQuery):
    try:
        # 1. Input Guardrail: Sanitize
        clean_query = guardrails.sanitize_input(query.query)
        
        # 2. RAG Logic
        rag_chain = llm_service.get_rag_chain()
        response = rag_chain.invoke({"input": clean_query})
        
        answer = response.get("answer", "No answer generated.")
        sources = []
        
        # Extract sources from context docs
        for doc in response.get("context", []):
            sources.append(Source(
                document_name=doc.metadata.get("source", "Desconocido"),
                page_number=doc.metadata.get("page_number", doc.metadata.get("page", 0)),
                content_snippet=doc.page_content[:250] + "...",
                relevance_score=0.0 
            ))

        chat_response = ChatResponse(answer=answer, sources=sources)

        # 3. Output Guardrail: Hallucination Check
        is_valid, reason = guardrails.validate_response(chat_response)
        if not is_valid:
            # We log the warning but might choose to still return the answer with a disclaimer
            # Or flag it in the response model if we add a 'warning' field
            print(f"GUARDRAIL ALERT: {reason}")
            answer += f"\n\n[ADVERTENCIA DEL SISTEMA: {reason}]"
            chat_response.answer = answer

        return chat_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
