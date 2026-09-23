"""
Runtime Context Module

This module provides execution context for the Runtime package.

Purpose
-------
Provide execution context management for the QuantsMind SDK.

Responsibilities
----------------
- Manage execution context
- Store context data
- Provide context access
- Handle context lifecycle

Dependencies
------------
typing (standard library)
logging (standard library)
uuid (standard library)
datetime (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.exceptions (runtime exceptions)
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from quantsmind.runtime.constants import RUNTIME_VERSION
from quantsmind.runtime.types import SessionID

logger = logging.getLogger(__name__)


class ExecutionContext:
    """Concrete implementation of execution context.

    This class provides context for execution operations.

    Attributes:
        _session_id: Session identifier
        _data: Context data
        _metadata: Context metadata
        _created_at: Creation timestamp
        _updated_at: Last update timestamp

    Example:
        >>> context = ExecutionContext(session_id="session_123")
    """

    def __init__(self, session_id: SessionID | None = None) -> None:
        """Initialize an ExecutionContext.

        Args:
            session_id: Optional session identifier

        Example:
            >>> context = ExecutionContext(session_id="session_123")
        """
        self._session_id = session_id or str(uuid.uuid4())
        self._data: dict[str, Any] = {}
        self._metadata: dict[str, Any] = {
            "runtime_version": RUNTIME_VERSION,
            "created_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
        }
        self._created_at = datetime.now(UTC).replace(tzinfo=None)
        self._updated_at = datetime.now(UTC).replace(tzinfo=None)
        logger.debug(f"Created execution context: {self._session_id}")

    @property
    def session_id(self) -> SessionID:
        """Get the session ID.

        Returns:
            Session identifier

        Example:
            >>> print(f"Session ID: {context.session_id}")
        """
        return self._session_id

    @property
    def data(self) -> dict[str, Any]:
        """Get the context data.

        Returns:
            Context data

        Example:
            >>> print(f"Data: {context.data}")
        """
        return self._data.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the context metadata.

        Returns:
            Context metadata

        Example:
            >>> print(f"Metadata: {context.metadata}")
        """
        return self._metadata.copy()

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp.

        Returns:
            Creation timestamp

        Example:
            >>> print(f"Created at: {context.created_at}")
        """
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get the last update timestamp.

        Returns:
            Last update timestamp

        Example:
            >>> print(f"Updated at: {context.updated_at}")
        """
        return self._updated_at

    def set(self, key: str, value: Any) -> None:
        """Set a context value.

        Args:
            key: Key
            value: Value

        Example:
            >>> context.set("user_id", "user_123")
        """
        self._data[key] = value
        self._updated_at = datetime.now(UTC).replace(tzinfo=None)
        logger.debug(f"Set context value: {key}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a context value.

        Args:
            key: Key
            default: Default value

        Returns:
            Value or default

        Example:
            >>> value = context.get("user_id")
        """
        return self._data.get(key, default)

    def has(self, key: str) -> bool:
        """Check if a key exists in context.

        Args:
            key: Key

        Returns:
            True if key exists, False otherwise

        Example:
            >>> if context.has("user_id"):
            ...     print("User ID exists")
        """
        return key in self._data

    def delete(self, key: str) -> None:
        """Delete a context value.

        Args:
            key: Key

        Example:
            >>> context.delete("user_id")
        """
        if key in self._data:
            del self._data[key]
            self._updated_at = datetime.now(UTC).replace(tzinfo=None)
            logger.debug(f"Deleted context value: {key}")

    def clear(self) -> None:
        """Clear all context data.

        Example:
            >>> context.clear()
        """
        self._data.clear()
        self._updated_at = datetime.now(UTC).replace(tzinfo=None)
        logger.debug("Cleared context data")

    def update(self, data: dict[str, Any]) -> None:
        """Update context with data.

        Args:
            data: Data to update

        Example:
            >>> context.update({"user_id": "user_123", "role": "admin"})
        """
        self._data.update(data)
        self._updated_at = datetime.now(UTC).replace(tzinfo=None)
        logger.debug(f"Updated context with {len(data)} keys")

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary.

        Returns:
            Dictionary representation

        Example:
            >>> data = context.to_dict()
        """
        return {
            "session_id": self._session_id,
            "data": self._data.copy(),
            "metadata": self._metadata.copy(),
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(context)
        """
        return f"ExecutionContext(session_id={self._session_id})"


# Export
__all__ = [
    "ExecutionContext",
]
