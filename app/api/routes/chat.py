from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatQuery, ChatResponse, Source
from app.services.llm import llm_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(query: ChatQuery):
    try:
        rag_chain = llm_service.get_rag_chain()
        response = rag_chain.invoke({"input": query.query})
        
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

        return ChatResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
