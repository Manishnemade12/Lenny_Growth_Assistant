"""Database repository for chat Message operations."""

import logging
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Message

logger = logging.getLogger(__name__)


class MessageRepository:
    """Repository handling Message creation and queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        session_id: UUID,
        role: str,
        content: str,
        source_citations: list[dict] | None = None,
        model_used: str | None = None,
        token_count: int = 0,
    ) -> Message:
        """Create and store message record."""
        msg = Message(
            session_id=session_id,
            role=role,
            content=content,
            source_citations=source_citations or [],
            model_used=model_used,
            token_count=token_count,
        )
        self.db.add(msg)
        await self.db.flush()
        return msg

    async def get_by_session(self, session_id: UUID, limit: int = 50) -> list[Message]:
        """Fetch messages belonging to session ordered by created_at."""
        stmt = (
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
