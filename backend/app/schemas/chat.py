"""Pydantic schemas for chat-related API contracts.

Defines request/response models for the /api/chat endpoint.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    """A reference to a transcript chunk used to ground an answer.

    Attributes:
        source_file: Filename of the source transcript.
        episode_title: Title of the podcast episode.
        speaker: Speaker name in the cited segment.
        excerpt: Brief excerpt from the source.
        similarity_score: Cosine similarity score (0-1).
    """

    source_file: str
    episode_title: str | None = None
    speaker: str | None = None
    excerpt: str
    similarity_score: float


class ChatRequest(BaseModel):
    """Request body for the chat endpoint.

    Attributes:
        session_id: UUID of the chat session.
        message: User message text (1-10000 characters).
        stream: Whether to use SSE streaming (default True).
    """

    session_id: UUID
    message: str = Field(..., min_length=1, max_length=10000)
    stream: bool = True


class ChatResponse(BaseModel):
    """Non-streaming response from the chat endpoint.

    Attributes:
        message_id: UUID of the stored assistant message.
        content: Full assistant response text.
        source_citations: List of transcript sources referenced.
        model_used: Provider/model identifier (e.g. "ollama/llama3.2").
        token_count: Approximate token count.
        created_at: When the response was generated.
    """

    message_id: UUID
    content: str
    source_citations: list[SourceCitation] = []
    model_used: str
    token_count: int
    created_at: datetime
