"""Repository classes for database operations."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import MessageModel, SessionModel


class SessionRepository:
    """
    Repository for session database operations.

    Handles CRUD operations for chat sessions with async/await pattern.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(
        self,
        session_id: UUID | None = None,
        user_id: str | None = None,
        metadata: dict | None = None,
    ) -> SessionModel:
        """
        Create a new session.

        Args:
            session_id: Optional session UUID (auto-generated if None)
            user_id: Optional user identifier
            metadata: Optional session metadata

        Returns:
            Created session model
        """
        session_model = SessionModel(
            id=session_id,
            user_id=user_id,
            metadata=metadata or {},
        )
        self.session.add(session_model)
        await self.session.commit()
        await self.session.refresh(session_model)
        return session_model

    async def get_by_id(self, session_id: UUID) -> SessionModel | None:
        """
        Get session by ID with all related messages.

        Args:
            session_id: Session UUID

        Returns:
            Session model or None if not found
        """
        stmt = select(SessionModel).where(SessionModel.id == session_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_recent_messages(
        self,
        session_id: UUID,
        limit: int = 5,
    ) -> list[MessageModel]:
        """
        Get recent messages for a session.

        Args:
            session_id: Session UUID
            limit: Maximum number of messages to retrieve

        Returns:
            List of message models ordered by creation time (most recent last)
        """
        stmt = (
            select(MessageModel)
            .where(MessageModel.session_id == session_id)
            .order_by(desc(MessageModel.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        messages = list(result.scalars().all())
        # Return in chronological order (oldest first)
        return list(reversed(messages))

    async def delete(self, session_id: UUID) -> bool:
        """
        Delete a session and all its messages (cascade).

        Args:
            session_id: Session UUID

        Returns:
            True if session was deleted, False if not found
        """
        stmt = delete(SessionModel).where(SessionModel.id == session_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def update_timestamp(self, session_id: UUID) -> SessionModel | None:
        """
        Update session's updated_at timestamp.

        Args:
            session_id: Session UUID

        Returns:
            Updated session model or None if not found
        """
        session_model = await self.get_by_id(session_id)
        if session_model:
            session_model.updated_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(session_model)
        return session_model


class MessageRepository:
    """
    Repository for message database operations.

    Handles CRUD operations for chat messages with async/await pattern.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(
        self,
        session_id: UUID,
        role: str,
        content: str,
        sources: list | None = None,
        latency_ms: float | None = None,
        top_k: int | None = None,
        query_type: str | None = None,
    ) -> MessageModel:
        """
        Create a new message.

        Args:
            session_id: Parent session UUID
            role: Message role ('user' or 'assistant')
            content: Message content
            sources: Optional list of retrieved sources
            latency_ms: Optional response latency in milliseconds
            top_k: Optional number of sources retrieved
            query_type: Optional query type ('chat' or 'search')

        Returns:
            Created message model
        """
        message = MessageModel(
            session_id=session_id,
            role=role,
            content=content,
            sources=sources,
            latency_ms=latency_ms,
            top_k=top_k,
            query_type=query_type,
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_session_history(
        self,
        session_id: UUID,
        limit: int = 5,
    ) -> list[dict[str, str]]:
        """
        Get session message history formatted for RAGEngine.

        Args:
            session_id: Session UUID
            limit: Maximum number of messages to retrieve

        Returns:
            List of message dictionaries with 'role' and 'content' keys,
            ordered chronologically (oldest first)
        """
        stmt = (
            select(MessageModel)
            .where(MessageModel.session_id == session_id)
            .order_by(desc(MessageModel.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        messages = list(result.scalars().all())
        # Return in chronological order (oldest first) and convert to dict
        return [msg.to_dict() for msg in reversed(messages)]
