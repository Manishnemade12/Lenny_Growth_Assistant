"""Database repository for Artifact CRUD operations."""

import logging
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Artifact

logger = logging.getLogger(__name__)


class ArtifactRepository:
    """Repository managing Artifact records."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        session_id: UUID,
        artifact_type: str,
        title: str,
        content: str,
        message_id: UUID | None = None,
    ) -> Artifact:
        """Create and store new artifact."""
        artifact = Artifact(
            session_id=session_id,
            message_id=message_id,
            type=artifact_type,
            title=title,
            content=content,
        )
        self.db.add(artifact)
        await self.db.flush()
        return artifact

    async def get_by_id(self, artifact_id: UUID) -> Artifact | None:
        """Fetch artifact by ID."""
        stmt = select(Artifact).where(Artifact.id == artifact_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()
