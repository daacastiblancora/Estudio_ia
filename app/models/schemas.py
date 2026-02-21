from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ChatQuery(BaseModel):
    query: str = Field(..., description="The user's question")
    collection_name: Optional[str] = Field(None, description="Optional collection to search in")
    session_id: Optional[str] = Field(None, description="Session ID to continue a conversation. Omit to start new.")

class Source(BaseModel):
    document_name: str
    page_number: Optional[int] = None
    content_snippet: str
    relevance_score: float

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    session_id: str = Field(..., description="Session ID for this conversation")

class IngestResponse(BaseModel):
    filename: str
    status: str
    message: str
    chunks_created: int

class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"

# --- Session Management Schemas ---

class MessageInfo(BaseModel):
    role: str
    content: str
    sources: Optional[str] = None
    created_at: datetime

class SessionInfo(BaseModel):
    id: str
    title: Optional[str] = None
    created_at: datetime
    message_count: int = 0
