"""SQLAlchemy models for session and message persistence."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class SessionModel(Base):
    """
    Session model for storing user chat sessions.

    Attributes:
        id: Unique session identifier (UUID)
        user_id: User identifier (nullable for anonymous sessions)
        created_at: Session creation timestamp
        updated_at: Session last update timestamp
        session_metadata: Additional session metadata (JSONB)
        messages: Relationship to associated messages
    """

    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Unique session identifier",
    )
    user_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="User identifier (nullable for anonymous)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment="Session creation timestamp",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Session last update timestamp",
    )
    session_metadata: Mapped[dict | None] = mapped_column(
        "metadata",  # Column name in database
        JSONB,
        nullable=True,
        comment="Additional session metadata",
    )

    # One-to-many relationship with messages (cascade delete)
    messages: Mapped[list["MessageModel"]] = relationship(
        "MessageModel",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="MessageModel.created_at",
    )

    # Indexes
    __table_args__ = (
        Index("ix_sessions_user_created", "user_id", "created_at"),
        Index("ix_sessions_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<SessionModel(id={self.id}, user_id={self.user_id}, "
            f"created_at={self.created_at})>"
        )


class MessageModel(Base):
    """
    Message model for storing chat messages within sessions.

    Attributes:
        id: Unique message identifier (auto-increment)
        session_id: Foreign key to parent session
        role: Message role ('user' or 'assistant')
        content: Message content
        created_at: Message creation timestamp
        sources: Retrieved sources for RAG responses (JSONB)
        latency_ms: Response latency in milliseconds
        top_k: Number of sources retrieved
        query_type: Query type ('chat' or 'search')
        session: Relationship to parent session
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Unique message identifier",
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to parent session",
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Message role (user or assistant)",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Message content",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment="Message creation timestamp",
    )
    sources: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Retrieved sources for RAG responses",
    )
    latency_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Response latency in milliseconds",
    )
    top_k: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of sources retrieved",
    )
    query_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Query type (chat or search)",
    )

    # Many-to-one relationship with session
    session: Mapped["SessionModel"] = relationship(
        "SessionModel",
        back_populates="messages",
        lazy="selectin",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant')",
            name="check_message_role",
        ),
        Index("ix_messages_session_created", "session_id", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<MessageModel(id={self.id}, session_id={self.session_id}, "
            f"role={self.role}, created_at={self.created_at})>"
        )

    def to_dict(self) -> dict[str, str]:
        """
        Convert message to dictionary format for RAGEngine.

        Returns:
            Dictionary with 'role' and 'content' keys
        """
        return {
            "role": self.role,
            "content": self.content,
        }
