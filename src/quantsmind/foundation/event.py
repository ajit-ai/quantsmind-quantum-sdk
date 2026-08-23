"""
Event Module

This module provides discrete timestamped occurrences within the QuantsMind SDK.
Event represents discrete, timestamped occurrences that may trigger or record interactions.

Purpose
-------
Provide discrete timestamped occurrences for entities and systems in the Foundation package.

Scientific Meaning
------------------
Event represents discrete occurrences: particle collisions, quantum measurements,
chemical reactions, biological events, financial transactions.

Responsibilities
----------------
- Manage event data
- Support event timestamps
- Enable event serialization
- Handle event types
- Support event queries

Dependencies
------------
typing (standard library)
logging (standard library)
datetime (standard library)
quantsmind.foundation.exceptions (exception hierarchy)
quantsmind.foundation.constants (constant values)
quantsmind.foundation.types (type definitions)
quantsmind.foundation.enums (enumeration types)
quantsmind.foundation.interfaces (abstract interfaces)

Future Extensions
-----------------
- Event causality tracking
- Event correlation
- Distributed event processing
- Event streams
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from quantsmind.foundation.enums import EventType
from quantsmind.foundation.exceptions import (
    InvalidEventError,
)
from quantsmind.foundation.interfaces import (
    Serializable,
    Validatable,
)
from quantsmind.foundation.types import (
    MetadataDict,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class Event(Serializable, Validatable):
    """Concrete implementation of discrete timestamped occurrences.

    This class provides a flexible event representation with support for
    various event types, timestamps, and associated data.

    Scientific Meaning
    ------------------
    In scientific computing, events represent discrete occurrences:
    particle collisions, quantum measurements, chemical reactions,
    biological events, financial transactions.

    Attributes:
        _id: Unique event identifier
        _event_type: Type of event
        _timestamp: Event timestamp
        _data: Event data
        _metadata: Additional metadata

    Example:
        >>> event = Event(event_type=EventType.STATE_CHANGE, data={"old": 1, "new": 2})
        >>> print(f"Event: {event.event_type} at {event.timestamp}")
    """

    def __init__(
        self,
        event_type: EventType = EventType.STATE_CHANGE,
        timestamp: datetime | None = None,
        data: dict[str, Any] | None = None,
        metadata: MetadataDict | None = None,
    ) -> None:
        """Initialize an Event.

        Args:
            event_type: Type of event
            timestamp: Event timestamp (defaults to current time)
            data: Event data dictionary
            metadata: Optional metadata dictionary

        Example:
            >>> event = Event(event_type=EventType.STATE_CHANGE, data={"old": 1, "new": 2})
        """
        self._id: str = str(uuid.uuid4())
        self._event_type: EventType = event_type
        self._timestamp: datetime = timestamp or datetime.utcnow()
        self._data: dict[str, Any] = data or {}
        self._metadata: MetadataDict = metadata or {}

        logger.debug(f"Created event: {event_type.value} at {self._timestamp}")

    @property
    def id(self) -> str:
        """Get the event ID.

        Returns:
            Event ID

        Example:
            >>> print(f"ID: {event.id}")
        """
        return self._id

    @property
    def event_type(self) -> EventType:
        """Get the event type.

        Returns:
            Event type

        Example:
            >>> print(f"Type: {event.event_type}")
        """
        return self._event_type

    @property
    def timestamp(self) -> datetime:
        """Get the event timestamp.

        Returns:
            Event timestamp

        Example:
            >>> print(f"Timestamp: {event.timestamp}")
        """
        return self._timestamp

    @property
    def data(self) -> dict[str, Any]:
        """Get the event data.

        Returns:
            Event data dictionary

        Example:
            >>> print(f"Data: {event.data}")
        """
        return self._data.copy()

    @property
    def metadata(self) -> MetadataDict:
        """Get the event metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> print(f"Metadata: {event.metadata}")
        """
        return self._metadata.copy()

    def set_data(self, key: str, value: Any) -> None:
        """Set event data.

        Args:
            key: Data key
            value: Data value

        Example:
            >>> event.set_data("result", 42)
        """
        self._data[key] = value
        logger.debug(f"Updated event data: {key} = {value}")

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get event data.

        Args:
            key: Data key
            default: Default value if key not found

        Returns:
            Data value or default

        Example:
            >>> result = event.get_data("result", 0)
        """
        return self._data.get(key, default)

    # Serializable interface implementation
    def serialize(self, format: str = "json") -> bytes:
        """Serialize the event to bytes.

        Args:
            format: Serialization format (currently only "json" supported)

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If format is not supported

        Example:
            >>> data = event.serialize(format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        data = {
            "id": self._id,
            "type": self._event_type.value,
            "timestamp": self._timestamp.isoformat(),
            "data": self._data,
            "metadata": self._metadata,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes, format: str = "json") -> Event:
        """Deserialize the event from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format (currently only "json" supported)

        Returns:
            Deserialized Event instance

        Raises:
            NotImplementedError: If format is not supported
            InvalidEventError: If data is invalid

        Example:
            >>> event = Event.deserialize(data, format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        try:
            obj = json.loads(data.decode("utf-8"))
            return cls(
                event_type=EventType(obj["type"]),
                timestamp=datetime.fromisoformat(obj["timestamp"]),
                data=obj.get("data"),
                metadata=obj.get("metadata"),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise InvalidEventError(f"Failed to deserialize event: {e}") from e

    def is_serializable(self) -> bool:
        """Check if the event is serializable.

        Returns:
            True (events are always serializable)

        Example:
            >>> if event.is_serializable():
            ...     data = event.serialize()
        """
        return True

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = Event.get_supported_formats()
        """
        return ["json"]

    # Validatable interface implementation
    def validate(self) -> ValidationResult:
        """Validate the event.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = event.validate()
        """
        errors: list[str] = []

        if not isinstance(self._event_type, EventType):
            errors.append("Event type must be an EventType")

        return (len(errors) == 0, errors)

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = event.validation_errors
        """
        is_valid, errors = self.validate()
        return errors if not is_valid else []

    @property
    def validation_warnings(self) -> list[str]:
        """Get validation warnings.

        Returns:
            List of warning messages (currently empty)

        Example:
            >>> warnings = event.validation_warnings
        """
        return []

    # Object protocol methods
    def __repr__(self) -> str:
        """Return string representation of the event.

        Returns:
            String representation

        Example:
            >>> repr(event)
        """
        return f"Event(type={self._event_type.value}, timestamp={self._timestamp})"

    def __str__(self) -> str:
        """Return string representation of the event.

        Returns:
            String representation

        Example:
            >>> str(event)
        """
        return f"{self._event_type.value} @ {self._timestamp}"

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> event1 == event2
        """
        if not isinstance(other, Event):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Return hash of the event.

        Returns:
            Hash value

        Example:
            >>> hash(event)
        """
        return hash(self._id)


# Export
__all__ = ["Event"]
