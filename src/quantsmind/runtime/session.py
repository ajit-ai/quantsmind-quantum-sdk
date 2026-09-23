"""
Runtime Session Module

This module provides session management for the Runtime package.

Purpose
-------
Provide session management for the QuantsMind SDK.

Responsibilities
----------------
- Manage runtime sessions
- Track session lifecycle
- Store session data
- Handle session cleanup

Dependencies
------------
typing (standard library)
logging (standard library)
uuid (standard library)
datetime (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
quantsmind.runtime.exceptions (runtime exceptions)
quantsmind.runtime.context (execution context)
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from quantsmind.runtime.constants import RUNTIME_VERSION
from quantsmind.runtime.context import ExecutionContext
from quantsmind.runtime.enums import ExecutionState
from quantsmind.runtime.exceptions import ValidationError
from quantsmind.runtime.types import SessionID

logger = logging.getLogger(__name__)


class RuntimeSession:
    """Concrete implementation of a runtime session.

    This class provides session management for execution operations.

    Attributes:
        _session_id: Session identifier
        _context: Execution context
        _state: Session state
        _created_at: Creation timestamp
        _closed_at: Close timestamp
        _metadata: Session metadata

    Example:
        >>> session = RuntimeSession()
        >>> session.initialize()
    """

    def __init__(self, session_id: SessionID | None = None) -> None:
        """Initialize a RuntimeSession.

        Args:
            session_id: Optional session identifier

        Example:
            >>> session = RuntimeSession()
        """
        self._session_id = session_id or str(uuid.uuid4())
        self._context = ExecutionContext(self._session_id)
        self._state = ExecutionState.CREATED
        self._created_at = datetime.now(UTC).replace(tzinfo=None)
        self._closed_at: datetime | None = None
        self._metadata: dict[str, Any] = {
            "runtime_version": RUNTIME_VERSION,
        }
        logger.debug(f"Created runtime session: {self._session_id}")

    @property
    def session_id(self) -> SessionID:
        """Get the session ID.

        Returns:
            Session identifier

        Example:
            >>> print(f"Session ID: {session.session_id}")
        """
        return self._session_id

    @property
    def context(self) -> ExecutionContext:
        """Get the execution context.

        Returns:
            Execution context

        Example:
            >>> context = session.context
        """
        return self._context

    @property
    def state(self) -> ExecutionState:
        """Get the session state.

        Returns:
            Session state

        Example:
            >>> print(f"State: {session.state}")
        """
        return self._state

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp.

        Returns:
            Creation timestamp

        Example:
            >>> print(f"Created at: {session.created_at}")
        """
        return self._created_at

    @property
    def closed_at(self) -> datetime | None:
        """Get the close timestamp.

        Returns:
            Close timestamp or None

        Example:
            >>> print(f"Closed at: {session.closed_at}")
        """
        return self._closed_at

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the session metadata.

        Returns:
            Session metadata

        Example:
            >>> print(f"Metadata: {session.metadata}")
        """
        return self._metadata.copy()

    @property
    def is_active(self) -> bool:
        """Check if the session is active.

        Returns:
            True if active, False otherwise

        Example:
            >>> if session.is_active:
            ...     print("Session is active")
        """
        return self._state in [ExecutionState.INITIALIZED, ExecutionState.RUNNING]

    def initialize(self) -> None:
        """Initialize the session.

        Raises:
            ValidationError: If session is already initialized

        Example:
            >>> session.initialize()
        """
        if self._state != ExecutionState.CREATED:
            raise ValidationError(f"Cannot initialize session in state: {self._state}")
        self._state = ExecutionState.INITIALIZED
        logger.info(f"Initialized session: {self._session_id}")

    def start(self) -> None:
        """Start the session.

        Raises:
            ValidationError: If session is not initialized

        Example:
            >>> session.start()
        """
        if self._state != ExecutionState.INITIALIZED:
            raise ValidationError(f"Cannot start session in state: {self._state}")
        self._state = ExecutionState.RUNNING
        logger.info(f"Started session: {self._session_id}")

    def pause(self) -> None:
        """Pause the session.

        Raises:
            ValidationError: If session is not running

        Example:
            >>> session.pause()
        """
        if self._state != ExecutionState.RUNNING:
            raise ValidationError(f"Cannot pause session in state: {self._state}")
        self._state = ExecutionState.PAUSED
        logger.info(f"Paused session: {self._session_id}")

    def resume(self) -> None:
        """Resume the session.

        Raises:
            ValidationError: If session is not paused

        Example:
            >>> session.resume()
        """
        if self._state != ExecutionState.PAUSED:
            raise ValidationError(f"Cannot resume session in state: {self._state}")
        self._state = ExecutionState.RUNNING
        logger.info(f"Resumed session: {self._session_id}")

    def close(self) -> None:
        """Close the session.

        Example:
            >>> session.close()
        """
        if self._state not in [ExecutionState.RUNNING, ExecutionState.PAUSED]:
            logger.warning(f"Closing session in state: {self._state}")
        self._state = ExecutionState.COMPLETED
        self._closed_at = datetime.now(UTC).replace(tzinfo=None)
        logger.info(f"Closed session: {self._session_id}")

    def cancel(self) -> None:
        """Cancel the session.

        Example:
            >>> session.cancel()
        """
        self._state = ExecutionState.CANCELLED
        self._closed_at = datetime.now(UTC).replace(tzinfo=None)
        logger.info(f"Cancelled session: {self._session_id}")

    def set_metadata(self, key: str, value: Any) -> None:
        """Set session metadata.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> session.set_metadata("user_id", "user_123")
        """
        self._metadata[key] = value
        logger.debug(f"Set session metadata: {key}")

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get session metadata.

        Args:
            key: Metadata key
            default: Default value

        Returns:
            Metadata value or default

        Example:
            >>> value = session.get_metadata("user_id")
        """
        return self._metadata.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """Convert session to dictionary.

        Returns:
            Dictionary representation

        Example:
            >>> data = session.to_dict()
        """
        return {
            "session_id": self._session_id,
            "state": self._state.value,
            "context": self._context.to_dict(),
            "created_at": self._created_at.isoformat(),
            "closed_at": self._closed_at.isoformat() if self._closed_at else None,
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(session)
        """
        return f"RuntimeSession(session_id={self._session_id}, state={self._state.value})"


# Export
__all__ = [
    "RuntimeSession",
]
