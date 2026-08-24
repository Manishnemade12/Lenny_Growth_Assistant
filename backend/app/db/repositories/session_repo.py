"""Database repository for chat Session CRUD operations."""

import logging
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Message, Session

logger = logging.getLogger(__name__)


class SessionRepository:
    """Repository handling Session entity queries and updates."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, title: str = "New Chat") -> Session:
        """Create and store new chat session."""
        session = Session(title=title)
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_by_id(self, session_id: UUID) -> Session | None:
        """Fetch session by ID."""
        stmt = select(Session).where(Session.id == session_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_all(self, limit: int = 50) -> list[dict]:
        """List sessions with message counts."""
        stmt = (
            select(
                Session.id,
                Session.title,
                Session.created_at,
                Session.updated_at,
                func.count(Message.id).label("message_count"),
            )
            .outerjoin(Message, Session.id == Message.session_id)
            .group_by(Session.id)
            .order_by(Session.updated_at.desc())
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        rows = res.all()
        return [
            {
                "id": r.id,
                "title": r.title,
                "message_count": r.message_count,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            }
            for r in rows
        ]

    async def delete(self, session_id: UUID) -> bool:
        """Delete session by ID."""
        session = await self.get_by_id(session_id)
        if session:
            await self.db.delete(session)
            return True
        return False
