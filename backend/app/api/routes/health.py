"""Health check endpoint for system status monitoring.

Reports the status of all critical subsystems: database, LLM provider,
and retrieval engine. Used by Docker health checks and monitoring.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.database import get_db
from app.db.models import TranscriptChunk
from app.schemas.common import HealthResponse

logger = logging.getLogger("app.api.health")

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System health check",
    description="Returns the status of database, LLM provider, and retrieval engine.",
)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Aggregate health status of all system components.

    Checks:
        - Database connectivity via a simple SELECT query
        - Transcript chunk count for retrieval readiness
        - LLM provider configuration (availability checked lazily)

    Args:
        db: Async database session (injected).

    Returns:
        HealthResponse with component statuses.
    """
    # ── Database check ───────────────────────────────────────
    db_status = "disconnected"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        logger.error("Health check: database unreachable", extra={"error": str(exc)})

    # ── Transcript count ─────────────────────────────────────
    transcript_count = 0
    retrieval_status = "not_ready"
    try:
        result = await db.execute(
            func.count(TranscriptChunk.id)
        )
        transcript_count = result.scalar() or 0
        retrieval_status = "ready" if transcript_count > 0 else "empty"
    except Exception:
        retrieval_status = "error"

    # ── LLM provider status (config-based, not live check) ──
    llm_provider = settings.ACTIVE_LLM_PROVIDER
    llm_model = _get_active_model()
    llm_status = "configured"

    # ── Aggregate status ─────────────────────────────────────
    overall = "healthy"
    if db_status != "connected":
        overall = "unhealthy"
    elif retrieval_status in ("empty", "not_ready"):
        overall = "degraded"

    return HealthResponse(
        status=overall,
        database=db_status,
        llm_provider=llm_provider,
        llm_model=llm_model,
        llm_status=llm_status,
        retrieval_engine=retrieval_status,
        transcript_count=transcript_count,
        timestamp=datetime.now(timezone.utc),
    )


def _get_active_model() -> str:
    """Return the model name for the currently active LLM provider."""
    model_map = {
        "ollama": settings.OLLAMA_MODEL,
        "anthropic": settings.ANTHROPIC_MODEL,
        "openai": settings.OPENAI_MODEL,
    }
    return model_map.get(settings.ACTIVE_LLM_PROVIDER, "unknown")
