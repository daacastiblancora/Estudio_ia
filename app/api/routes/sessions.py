from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import List

from app.core.database import get_session
from app.api.deps import get_current_active_user
from app.models.sql_schemas import User, ChatSession, ChatMessage
from app.models.schemas import SessionInfo, MessageInfo

router = APIRouter()


@router.get("/sessions", response_model=List[SessionInfo])
async def list_sessions(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """List all chat sessions for the authenticated user, newest first."""
    # Subquery: count messages per session
    msg_count = (
        select(
            ChatMessage.session_id,
            func.count(ChatMessage.id).label("message_count"),
        )
        .group_by(ChatMessage.session_id)
        .subquery()
    )

    stmt = (
        select(ChatSession, msg_count.c.message_count)
        .outerjoin(msg_count, ChatSession.id == msg_count.c.session_id)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.created_at.desc())
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        SessionInfo(
            id=session.id,
            title=session.title,
            created_at=session.created_at,
            message_count=count or 0,
        )
        for session, count in rows
    ]


@router.get("/sessions/{session_id}/messages", response_model=List[MessageInfo])
async def get_session_messages(
    session_id: str,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Get all messages for a specific session (must belong to the user)."""
    # Verify session belongs to user
    session_stmt = select(ChatSession).where(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id,
    )
    result = await db.execute(session_stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Fetch messages
    msg_stmt = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    result = await db.execute(msg_stmt)
    messages = result.scalars().all()

    return [
        MessageInfo(
            role=msg.role,
            content=msg.content,
            sources=msg.sources,
            created_at=msg.created_at,
        )
        for msg in messages
    ]


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a session and all its messages."""
    # Verify session belongs to user
    session_stmt = select(ChatSession).where(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id,
    )
    result = await db.execute(session_stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Delete messages first, then session
    await db.execute(
        delete(ChatMessage).where(ChatMessage.session_id == session_id)
    )
    await db.delete(session)
    await db.commit()
