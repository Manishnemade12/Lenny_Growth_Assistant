"""FastAPI Session CRUD API routes."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.repositories.message_repo import MessageRepository
from app.db.repositories.session_repo import SessionRepository
from app.schemas.session import SessionCreate, SessionDetailResponse, SessionResponse

router = APIRouter()


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: SessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new chat session."""
    repo = SessionRepository(db)
    session = await repo.create(title=payload.title or "New Chat")
    return SessionResponse(
        id=session.id,
        title=session.title,
        message_count=0,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """List all sessions ordered by recency."""
    repo = SessionRepository(db)
    return await repo.list_all()


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get session details with message history."""
    session_repo = SessionRepository(db)
    msg_repo = MessageRepository(db)

    session = await session_repo.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = await msg_repo.get_by_session(session_id)
    formatted_messages = [
        {
            "message_id": m.id,
            "content": m.content,
            "source_citations": m.source_citations or [],
            "model_used": m.model_used or "unknown",
            "token_count": m.token_count,
            "created_at": m.created_at,
        }
        for m in messages
    ]

    return SessionDetailResponse(
        id=session.id,
        title=session.title,
        message_count=len(messages),
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=formatted_messages,
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a session by ID."""
    repo = SessionRepository(db)
    success = await repo.delete(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
