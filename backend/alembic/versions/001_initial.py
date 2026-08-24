"""Initial schema: sessions, messages, artifacts, transcript_chunks.

Revision ID: 001_initial
Revises: None
Create Date: 2026-08-24
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables with savepoint vector check."""
    bind = op.get_bind()
    has_vector = False
    
    # Try savepoint execution to test pgvector extension availability without aborting transaction
    try:
        sp = bind.begin_nested()
        bind.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
        sp.commit()
        has_vector = True
    except Exception:
        sp.rollback()
        has_vector = False

    # ── sessions ─────────────────────────────────────────────
    op.create_table(
        "sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.String(255), server_default="New Chat"),
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_sessions_created_at", "sessions", ["created_at"], postgresql_using="btree")

    # ── messages ─────────────────────────────────────────────
    op.create_table(
        "messages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", UUID(as_uuid=True), sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("source_citations", JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("model_used", sa.String(100)),
        sa.Column("token_count", sa.Integer, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name="ck_message_role"),
    )
    op.create_index("idx_messages_session_id", "messages", ["session_id"])
    op.create_index("idx_messages_session_created", "messages", ["session_id", "created_at"])

    # ── artifacts ────────────────────────────────────────────
    op.create_table(
        "artifacts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", UUID(as_uuid=True), sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("message_id", UUID(as_uuid=True), sa.ForeignKey("messages.id", ondelete="SET NULL"), nullable=True),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("title", sa.String(255), server_default="Untitled Artifact"),
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("type IN ('markdown', 'html')", name="ck_artifact_type"),
    )
    op.create_index("idx_artifacts_session_id", "artifacts", ["session_id"])

    # ── transcript_chunks ────────────────────────────────────
    embedding_col = Vector(768) if has_vector else JSONB
    op.create_table(
        "transcript_chunks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source_file", sa.String(500), nullable=False),
        sa.Column("episode_title", sa.String(500)),
        sa.Column("speaker", sa.String(255)),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("embedding", embedding_col),
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_chunks_source", "transcript_chunks", ["source_file"])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table("artifacts")
    op.drop_table("messages")
    op.drop_table("transcript_chunks")
    op.drop_table("sessions")
