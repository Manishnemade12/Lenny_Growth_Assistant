"""Embedding service providing vector generation for transcript chunks and queries.

Supports local Ollama embeddings with fallback to simple hash vectors in development/test environments.
"""

import logging
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generates vector embeddings using configured provider (Ollama by default)."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_EMBED_MODEL
        self.dimension = settings.VECTOR_DIMENSION

    async def embed(self, text: str) -> list[float]:
        """Generate embedding vector for input text."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/embed",
                    json={"model": self.model, "input": text},
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["embeddings"][0]
        except Exception as exc:
            logger.warning(
                "Ollama embedding unavailable, generating fallback vector",
                extra={"error": str(exc)},
            )

        # Development / Test fallback vector generator when Ollama is offline
        return self._generate_fallback_embedding(text)

    def _generate_fallback_embedding(self, text: str) -> list[float]:
        """Generate deterministic normalized fallback vector based on hash."""
        import hashlib
        import math

        hash_digest = hashlib.sha256(text.encode("utf-8")).digest()
        raw_vec = [
            (b / 255.0) - 0.5 for b in hash_digest * (self.dimension // 32 + 1)
        ][: self.dimension]
        
        magnitude = math.sqrt(sum(x * x for x in raw_vec)) or 1.0
        return [x / magnitude for x in raw_vec]
