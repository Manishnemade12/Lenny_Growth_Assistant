"""Vector retriever performing semantic similarity search against pgvector."""

import logging
from sqlalchemy import text
from app.config import settings
from app.db.database import async_session_factory
from app.rag.embeddings import EmbeddingService

logger = logging.getLogger(__name__)


class Retriever:
    """Vector similarity retriever using cosine distance on pgvector with text fallback."""

    def __init__(self):
        self.embedding_service = EmbeddingService()

    async def search(
        self,
        query: str,
        top_k: int | None = None,
        similarity_threshold: float | None = None,
    ) -> list[dict]:
        """Search transcript_chunks for matches to query vector."""
        limit = top_k or settings.TOP_K_RETRIEVAL
        threshold = similarity_threshold or settings.SIMILARITY_THRESHOLD

        query_embedding = await self.embedding_service.embed(query)

        async with async_session_factory() as db:
            # Try vector cosine similarity using CAST(:query_vec AS vector)
            try:
                result = await db.execute(
                    text("""
                        SELECT 
                            id, source_file, episode_title, speaker, 
                            chunk_index, content, metadata,
                            1 - (embedding <=> CAST(:query_vec AS vector)) as score
                        FROM transcript_chunks
                        WHERE 1 - (embedding <=> CAST(:query_vec AS vector)) > :threshold
                        ORDER BY embedding <=> CAST(:query_vec AS vector)
                        LIMIT :limit
                    """),
                    {
                        "query_vec": str(query_embedding),
                        "threshold": threshold,
                        "limit": limit,
                    },
                )
                rows = result.fetchall()
            except Exception as e:
                logger.warning(f"Vector search falling back to text search: {e}")
                # Text similarity fallback using ILIKE keywords
                keywords = [w for w in query.split() if len(w) > 3][:3]
                if keywords:
                    pattern = f"%{keywords[0]}%"
                    result = await db.execute(
                        text("""
                            SELECT 
                                id, source_file, episode_title, speaker, 
                                chunk_index, content, metadata,
                                0.8 as score
                            FROM transcript_chunks
                            WHERE content ILIKE :pattern
                            LIMIT :limit
                        """),
                        {"pattern": pattern, "limit": limit},
                    )
                    rows = result.fetchall()
                else:
                    rows = []

        chunks = [
            {
                "id": str(row.id),
                "source_file": row.source_file,
                "episode_title": row.episode_title,
                "speaker": row.speaker,
                "chunk_index": row.chunk_index,
                "content": row.content,
                "score": float(row.score),
                "metadata": row.metadata,
            }
            for row in rows
        ]

        logger.info(
            "Retriever search completed",
            extra={"query": query[:50], "results_count": len(chunks)},
        )
        return chunks
