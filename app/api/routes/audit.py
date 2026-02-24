from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_session
from app.api.deps import require_role
from app.models.sql_schemas import User, ChatSession, ChatMessage

router = APIRouter()


class AuditEntry(BaseModel):
    """One Q&A interaction for auditing purposes."""
    session_id: str
    user_email: str
    user_role: str
    question: str
    answer: str
    sources: Optional[str] = None
    timestamp: datetime


class AuditSummary(BaseModel):
    """High-level stats for the audit dashboard."""
    total_users: int
    total_sessions: int
    total_messages: int
    active_users: int  # Users with at least 1 session


@router.get("/audit/stats", response_model=AuditSummary)
async def audit_stats(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin")),
):
    """Get high-level usage statistics (admin only)."""
    users_count = await db.execute(select(func.count(User.id)))
    sessions_count = await db.execute(select(func.count(ChatSession.id)))
    messages_count = await db.execute(select(func.count(ChatMessage.id)))
    active_users = await db.execute(
        select(func.count(func.distinct(ChatSession.user_id)))
    )

    return AuditSummary(
        total_users=users_count.scalar_one(),
        total_sessions=sessions_count.scalar_one(),
        total_messages=messages_count.scalar_one(),
        active_users=active_users.scalar_one(),
    )


@router.get("/audit/logs", response_model=List[AuditEntry])
async def audit_logs(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin")),
    limit: int = Query(50, ge=1, le=500, description="Max entries to return"),
    user_email: Optional[str] = Query(None, description="Filter by user email"),
):
    """
    Query all chat interactions across all users (admin only).
    Returns pairs of (question, answer) with user info and timestamps.
    Newest first. Optional filter by user email.
    """
    # Get user messages (questions) joined with their session + user
    user_msgs = (
        select(
            ChatMessage.session_id,
            ChatMessage.content.label("question"),
            ChatMessage.created_at,
            User.email.label("user_email"),
            User.role.label("user_role"),
        )
        .join(ChatSession, ChatMessage.session_id == ChatSession.id)
        .join(User, ChatSession.user_id == User.id)
        .where(ChatMessage.role == "user")
    )

    if user_email:
        user_msgs = user_msgs.where(User.email == user_email)

    user_msgs = user_msgs.order_by(ChatMessage.created_at.desc()).limit(limit)
    result = await db.execute(user_msgs)
    questions = result.all()

    entries = []
    for q in questions:
        # Find the corresponding AI answer (next message in the session after this question)
        answer_stmt = (
            select(ChatMessage)
            .where(
                ChatMessage.session_id == q.session_id,
                ChatMessage.role == "assistant",
                ChatMessage.created_at >= q.created_at,
            )
            .order_by(ChatMessage.created_at)
            .limit(1)
        )
        answer_result = await db.execute(answer_stmt)
        ai_msg = answer_result.scalar_one_or_none()

        entries.append(AuditEntry(
            session_id=q.session_id,
            user_email=q.user_email,
            user_role=q.user_role,
            question=q.question,
            answer=ai_msg.content if ai_msg else "(sin respuesta)",
            sources=ai_msg.sources if ai_msg else None,
            timestamp=q.created_at,
        ))

    return entries
