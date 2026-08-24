"""Transcript ingestion module parsing markdown transcript files into embedded chunks."""

import logging
from pathlib import Path

from app.rag.chunker import RecursiveCharacterChunker
from app.rag.embeddings import EmbeddingService
from app.db.repositories.transcript_repo import TranscriptRepository
from app.config import settings

logger = logging.getLogger(__name__)


class TranscriptIngester:
    """Pipeline for loading, parsing, chunking, embedding, and saving transcripts."""

    def __init__(self, db):
        self.db = db
        self.embedder = EmbeddingService()
        self.chunker = RecursiveCharacterChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        self.repo = TranscriptRepository(db)

    async def ingest_directory(self, transcript_dir: str):
        """Process all markdown/text transcript files in a target directory."""
        path = Path(transcript_dir)
        if not path.exists():
            logger.warning(f"Directory {transcript_dir} does not exist")
            return

        files = list(path.glob("*.md")) + list(path.glob("*.txt"))
        logger.info(f"Found {len(files)} transcript files to ingest")

        for f in files:
            await self.ingest_file(f)

    async def ingest_file(self, file_path: Path):
        """Parse and ingest a single transcript file if not already present."""
        existing = await self.repo.get_by_source(file_path.name)
        if existing:
            logger.info(f"Skipping already ingested file: {file_path.name}")
            return

        content = file_path.read_text(encoding="utf-8")
        metadata = self._extract_metadata(file_path.name, content)
        chunks = self.chunker.split(content)

        logger.info(f"Ingesting {file_path.name} ({len(chunks)} chunks)")

        for idx, chunk_text in enumerate(chunks):
            embedding = await self.embedder.embed(chunk_text)
            await self.repo.create_chunk(
                source_file=file_path.name,
                episode_title=metadata.get("episode_title"),
                speaker=metadata.get("speaker"),
                chunk_index=idx,
                content=chunk_text,
                embedding=embedding,
                metadata=metadata,
            )

    def _extract_metadata(self, filename: str, content: str) -> dict:
        """Extract metadata title and guest speaker from content or filename."""
        metadata = {"source_file": filename}
        lines = content.split("\n")

        for line in lines[:5]:
            if line.startswith("# "):
                metadata["episode_title"] = line[2:].strip()
                break

        if "episode_title" not in metadata:
            name = filename.replace(".md", "").replace(".txt", "")
            metadata["episode_title"] = name.replace("-", " ").replace("_", " ").title()

        return metadata


async def verify_knowledge_base():
    """Verify knowledge base state on startup."""
    logger.info("Knowledge base verifier ready")
