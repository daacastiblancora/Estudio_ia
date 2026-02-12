from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
import uuid

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    role: str = Field(default="user") # user, admin
    
    sessions: List["ChatSession"] = Relationship(back_populates="user")

class ChatSession(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    title: Optional[str] = Field(default="New Chat")
    
    messages: List["ChatMessage"] = Relationship(back_populates="session")
    user: Optional[User] = Relationship(back_populates="sessions")

class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="chatsession.id")
    role: str = Field(index=True) # user, ai
    content: str
    sources: Optional[str] = Field(default=None) # JSON string of sources
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    session: ChatSession = Relationship(back_populates="messages")
