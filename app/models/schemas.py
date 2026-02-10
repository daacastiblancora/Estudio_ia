from typing import List, Optional
from pydantic import BaseModel, Field

class ChatQuery(BaseModel):
    query: str = Field(..., description="The user's question")
    collection_name: Optional[str] = Field(None, description="Optional collection to search in")

class Source(BaseModel):
    document_name: str
    page_number: Optional[int] = None
    content_snippet: str
    relevance_score: float

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]

class IngestResponse(BaseModel):
    filename: str
    status: str
    message: str
    chunks_created: int

class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"
