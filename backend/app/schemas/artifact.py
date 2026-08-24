"""Pydantic schemas for artifact API contracts.

Defines request/response models for the /api/artifacts endpoints.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ArtifactCreate(BaseModel):
    """Request body for generating a new artifact.

    Attributes:
        session_id: UUID of the parent chat session.
        type: Artifact type — 'markdown' or 'html'.
        prompt: User prompt describing the desired artifact.
        context_message_ids: Optional list of message UUIDs for context.
    """

    session_id: UUID
    type: str = Field(..., pattern=r"^(markdown|html)$")
    prompt: str
    context_message_ids: list[UUID] = []


class ArtifactResponse(BaseModel):
    """Response body for a generated artifact.

    Attributes:
        id: Unique artifact identifier.
        type: 'markdown' or 'html'.
        title: Display title of the artifact.
        content: Full artifact content.
        created_at: When the artifact was generated.
    """

    id: UUID
    type: str
    title: str
    content: str
    created_at: datetime
