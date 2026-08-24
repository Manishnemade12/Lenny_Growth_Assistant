"""Async database engine and session factory.

Uses SQLAlchemy 2.0 async with asyncpg driver for PostgreSQL.
Compatible with local PostgreSQL and cloud-hosted Supabase PostgreSQL.
"""

import logging
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

logger = logging.getLogger(__name__)

# Configure connect args for Supabase / PgBouncer compatibility
connect_args = {}
db_url = settings.DATABASE_URL.lower()

if "supabase" in db_url or "pooler" in db_url or ":6543" in db_url:
    # Supabase PgBouncer pooler mode requires disabling prepared statements in asyncpg
    connect_args["prepared_statement_cache_size"] = 0
    logger.info("Detected Supabase/PgBouncer pooler URL; disabled prepared_statement_cache_size")

engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.LOG_LEVEL == "DEBUG",
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """FastAPI dependency that yields an async database session.

    Commits on success, rolls back on exception, always closes.

    Yields:
        AsyncSession: An active database session.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Verify database connectivity on startup."""
    try:
        async with engine.begin() as conn:
            await conn.execute(
                __import__("sqlalchemy").text("SELECT 1")
            )
        logger.info("Database connection established")
    except Exception as exc:
        logger.error(
            "Database connection failed",
            extra={"error": str(exc)},
        )
        raise


async def close_db() -> None:
    """Dispose of the database engine on shutdown."""
    await engine.dispose()
    logger.info("Database connection closed")
