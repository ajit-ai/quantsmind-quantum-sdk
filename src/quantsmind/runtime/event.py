"""
Runtime Event Module

This module provides event management for the Runtime package.

Purpose
-------
Provide event management for the QuantsMind SDK.

Responsibilities
----------------
- Define event structure
- Support event metadata
- Handle event validation
- Support event serialization

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
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from quantsmind.runtime.constants import RUNTIME_VERSION
from quantsmind.runtime.enums import EventType
from quantsmind.runtime.types import EventID, EventPayload

logger = logging.getLogger(__name__)


class Event:
    """Concrete implementation of an event.

    This class provides event management capabilities.

    Attributes:
        _event_id: Event identifier
        _event_type: Event type
        _payload: Event payload
        _timestamp: Event timestamp
        _metadata: Event metadata

    Example:
        >>> event = Event(EventType.ENTITY_CREATED, {"task_id": "task_123"})
        >>> event.payload["task_id"]
    """

    def __init__(
        self,
        event_type: EventType,
        payload: EventPayload | None = None,
        event_id: EventID | None = None,
    ) -> None:
        """Initialize an Event.

        Args:
            event_type: Event type
            payload: Event payload
            event_id: Optional event identifier

        Example:
            >>> event = Event(EventType.ENTITY_CREATED, {"task_id": "task_123"})
        """
        self._event_id = event_id or str(uuid.uuid4())
        self._event_type = event_type
        self._payload = payload or {}
        self._timestamp = datetime.now(UTC).replace(tzinfo=None)
        self._metadata: dict[str, Any] = {
            "runtime_version": RUNTIME_VERSION,
        }
        logger.debug(f"Created event: {self._event_id} of type {event_type.value}")

    @property
    def event_id(self) -> EventID:
        """Get the event ID.

        Returns:
            Event identifier

        Example:
            >>> print(f"Event ID: {event.event_id}")
        """
        return self._event_id

    @property
    def event_type(self) -> EventType:
        """Get the event type.

        Returns:
            Event type

        Example:
            >>> print(f"Event type: {event.event_type}")
        """
        return self._event_type

    @property
    def payload(self) -> EventPayload:
        """Get the event payload.

        Returns:
            Event payload

        Example:
            >>> print(f"Payload: {event.payload}")
        """
        return self._payload.copy()

    @property
    def timestamp(self) -> datetime:
        """Get the event timestamp.

        Returns:
            Event timestamp

        Example:
            >>> print(f"Timestamp: {event.timestamp}")
        """
        return self._timestamp

    def set_metadata(self, key: str, value: Any) -> None:
        """Set event metadata.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> event.set_metadata("source", "executor")
        """
        self._metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get event metadata.

        Args:
            key: Metadata key
            default: Default value

        Returns:
            Metadata value or default

        Example:
            >>> value = event.get_metadata("source")
        """
        return self._metadata.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary.

        Returns:
            Dictionary representation

        Example:
            >>> data = event.to_dict()
        """
        return {
            "event_id": self._event_id,
            "event_type": self._event_type.value,
            "payload": self._payload.copy(),
            "timestamp": self._timestamp.isoformat(),
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(event)
        """
        return f"Event(event_id={self._event_id}, type={self._event_type.value})"


# Export
__all__ = [
    "Event",
]
