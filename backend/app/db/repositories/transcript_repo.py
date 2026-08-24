"""Transcript repository for storing and querying chunked transcript vectors."""

import logging
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import TranscriptChunk

logger = logging.getLogger(__name__)


class TranscriptRepository:
    """Repository handling CRUD operations for transcript chunks in PostgreSQL + pgvector."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_source(self, source_file: str) -> list[TranscriptChunk]:
        """Fetch all chunks belonging to a specific source file."""
        stmt = select(TranscriptChunk).where(TranscriptChunk.source_file == source_file)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_chunk(
        self,
        source_file: str,
        episode_title: str | None,
        speaker: str | None,
        chunk_index: int,
        content: str,
        embedding: list[float],
        metadata: dict | None = None,
    ) -> TranscriptChunk:
        """Create and store a single transcript chunk record."""
        chunk = TranscriptChunk(
            source_file=source_file,
            episode_title=episode_title,
            speaker=speaker,
            chunk_index=chunk_index,
            content=content,
            embedding=embedding,
            metadata_=metadata or {},
        )
        self.db.add(chunk)
        await self.db.flush()
        return chunk
