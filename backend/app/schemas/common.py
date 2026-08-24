"""Common Pydantic schemas used across the application.

Includes error responses and health check models.
"""

from datetime import datetime

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response format for all API errors.

    Attributes:
        error: Human-readable error message.
        code: Machine-readable error code (e.g. VALIDATION_ERROR).
        detail: Optional additional context about the error.
        timestamp: ISO 8601 timestamp of when the error occurred.
    """

    error: str
    code: str
    detail: str | None = None
    timestamp: datetime


class HealthResponse(BaseModel):
    """System health check response.

    Attributes:
        status: Overall system status (healthy, degraded, unhealthy).
        database: Database connection status.
        llm_provider: Name of the active LLM provider.
        llm_model: Name of the active model.
        llm_status: LLM provider availability status.
        retrieval_engine: RAG retrieval engine status.
        transcript_count: Number of indexed transcript chunks.
        timestamp: ISO 8601 timestamp.
    """

    status: str
    database: str
    llm_provider: str
    llm_model: str
    llm_status: str
    retrieval_engine: str
    transcript_count: int
    timestamp: datetime
