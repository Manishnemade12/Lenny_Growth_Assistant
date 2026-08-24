"""SQLAlchemy ORM models for all database tables.

Tables:
    - sessions: Chat sessions with metadata
    - messages: Individual messages within sessions
    - artifacts: Generated Markdown/HTML artifacts
    - transcript_chunks: Embedded transcript segments for RAG
"""

import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship

from app.config import settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class Session(Base):
    """A chat session containing messages and artifacts.

    Attributes:
        id: Unique session identifier (UUID v4).
        title: Human-readable session title.
        metadata_: Arbitrary JSON metadata.
        created_at: When the session was created (UTC).
        updated_at: When the session was last modified (UTC).
    """

    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), default="New Chat")
    metadata_ = Column("metadata", JSONB, default=dict)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    messages = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )
    artifacts = relationship(
        "Artifact",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class Message(Base):
    """A single message within a chat session.

    Attributes:
        id: Unique message identifier (UUID v4).
        session_id: FK to the parent session.
        role: One of 'user', 'assistant', or 'system'.
        content: The message text content.
        source_citations: JSON array of source references.
        metadata_: Arbitrary JSON metadata.
        model_used: Which LLM model generated this (e.g. "ollama/llama3.2").
        token_count: Approximate token count of the response.
        created_at: When the message was created (UTC).
    """

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    source_citations = Column(JSONB, default=list)
    metadata_ = Column("metadata", JSONB, default=dict)
    model_used = Column(String(100))
    token_count = Column(Integer, default=0)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant', 'system')",
            name="ck_message_role",
        ),
    )

    session = relationship("Session", back_populates="messages")


class Artifact(Base):
    """A generated Markdown or HTML artifact from a conversation.

    Attributes:
        id: Unique artifact identifier (UUID v4).
        session_id: FK to the parent session.
        message_id: Optional FK to the message that triggered generation.
        type: 'markdown' or 'html'.
        content: The full artifact content.
        title: Display title.
        metadata_: Arbitrary JSON metadata.
        created_at: When the artifact was created (UTC).
    """

    __tablename__ = "artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    message_id = Column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
    )
    type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    title = Column(String(255), default="Untitled Artifact")
    metadata_ = Column("metadata", JSONB, default=dict)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        CheckConstraint(
            "type IN ('markdown', 'html')",
            name="ck_artifact_type",
        ),
    )

    session = relationship("Session", back_populates="artifacts")


class TranscriptChunk(Base):
    """An embedded chunk of a Lenny's Podcast transcript for RAG retrieval.

    Attributes:
        id: Unique chunk identifier (UUID v4).
        source_file: Filename of the source transcript.
        episode_title: Extracted episode title.
        speaker: Primary speaker in this chunk.
        chunk_index: Sequential index within the source file.
        content: The text content of this chunk.
        embedding: Vector embedding for similarity search (pgvector).
        metadata_: Arbitrary JSON metadata.
        created_at: When the chunk was created (UTC).
    """

    __tablename__ = "transcript_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_file = Column(String(500), nullable=False)
    episode_title = Column(String(500))
    speaker = Column(String(255))
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(settings.VECTOR_DIMENSION))
    metadata_ = Column("metadata", JSONB, default=dict)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
