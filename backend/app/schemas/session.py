"""Pydantic schemas for session management API contracts.

Defines request/response models for the /api/sessions endpoints.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.chat import ChatResponse


class SessionCreate(BaseModel):
    """Request body for creating a new chat session.

    Attributes:
        title: Optional session title (defaults to 'New Chat').
    """

    title: str | None = "New Chat"


class SessionResponse(BaseModel):
    """Summary response for a chat session (used in list views).

    Attributes:
        id: Unique session identifier.
        title: Session display title.
        message_count: Total number of messages in the session.
        created_at: When the session was created.
        updated_at: When the session was last modified.
    """

    id: UUID
    title: str
    message_count: int = 0
    created_at: datetime
    updated_at: datetime


class SessionDetailResponse(SessionResponse):
    """Detailed session response including full message history.

    Attributes:
        messages: List of all messages in chronological order.
    """

    messages: list[ChatResponse] = []
