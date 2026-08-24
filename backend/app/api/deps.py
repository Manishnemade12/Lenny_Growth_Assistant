"""FastAPI dependency injection providers.

Centralized dependency definitions used across API routes.
"""

from app.db.database import get_db

__all__ = ["get_db"]
