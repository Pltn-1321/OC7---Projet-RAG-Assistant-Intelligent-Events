"""Initial schema: create sessions and messages tables

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-02-04 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create sessions and messages tables with all constraints and indexes.

    Tables created:
    - sessions: Store user chat sessions
    - messages: Store individual messages within sessions
    """
    # Create sessions table
    op.create_table(
        "sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="Unique session identifier",
        ),
        sa.Column(
            "user_id",
            sa.String(length=255),
            nullable=True,
            comment="User identifier (nullable for anonymous)",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            comment="Session creation timestamp",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            comment="Session last update timestamp",
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Additional session metadata",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessions")),
        comment="User chat sessions",
    )

    # Create indexes for sessions table
    op.create_index(
        op.f("ix_sessions_user_id"),
        "sessions",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_sessions_user_created",
        "sessions",
        ["user_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_sessions_created_at",
        "sessions",
        ["created_at"],
        unique=False,
    )

    # Create messages table
    op.create_table(
        "messages",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
            comment="Unique message identifier",
        ),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="Foreign key to parent session",
        ),
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            comment="Message role (user or assistant)",
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
            comment="Message content",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            comment="Message creation timestamp",
        ),
        sa.Column(
            "sources",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Retrieved sources for RAG responses",
        ),
        sa.Column(
            "latency_ms",
            sa.Float(),
            nullable=True,
            comment="Response latency in milliseconds",
        ),
        sa.Column(
            "top_k",
            sa.Integer(),
            nullable=True,
            comment="Number of sources retrieved",
        ),
        sa.Column(
            "query_type",
            sa.String(length=20),
            nullable=True,
            comment="Query type (chat or search)",
        ),
        sa.CheckConstraint(
            "role IN ('user', 'assistant')",
            name=op.f("check_message_role"),
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.id"],
            name=op.f("fk_messages_session_id_sessions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_messages")),
        comment="Chat messages within sessions",
    )

    # Create indexes for messages table
    op.create_index(
        op.f("ix_messages_session_id"),
        "messages",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        "ix_messages_session_created",
        "messages",
        ["session_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    """
    Drop messages and sessions tables.

    Note: This will delete all session and message data.
    """
    # Drop messages table (must be dropped first due to foreign key)
    op.drop_index("ix_messages_session_created", table_name="messages")
    op.drop_index(op.f("ix_messages_session_id"), table_name="messages")
    op.drop_table("messages")

    # Drop sessions table
    op.drop_index("ix_sessions_created_at", table_name="sessions")
    op.drop_index("ix_sessions_user_created", table_name="sessions")
    op.drop_index(op.f("ix_sessions_user_id"), table_name="sessions")
    op.drop_table("sessions")
