"""CLI script for ingesting podcast transcripts into the vector database."""

import asyncio
import logging
from app.db.database import async_session_factory
from app.rag.ingestion import TranscriptIngester

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting transcript ingestion script...")
    async with async_session_factory() as db:
        ingester = TranscriptIngester(db)
        await ingester.ingest_directory("data/transcripts")
        await db.commit()
    logger.info("Transcript ingestion complete.")


if __name__ == "__main__":
    asyncio.run(main())
