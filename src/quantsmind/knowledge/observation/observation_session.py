"""
Observation Session Module

This module provides observation session definitions for the Knowledge package.

Purpose
-------
Provide observation session management for grouping observations.

Responsibilities
----------------
- Define observation session structure
- Support observation session operations
- Support observation session validation
- Support observation session metadata

Dependencies
------------
typing (standard library)
datetime (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from quantsmind.knowledge.exceptions import ObservationError
from quantsmind.knowledge.types import ValidationResult


class ObservationSession:
    """Concrete implementation of an observation session.

    This class provides observation session functionality for grouping related observations.

    Attributes:
        _id: Session ID
        _name: Session name
        _observer: Observer ID
        _start_time: Start timestamp
        _end_time: End timestamp
        _observation_ids: Observation IDs in session
        _metadata: Session metadata

    Example:
        >>> session = ObservationSession("session_001", "Experiment 1", "observer_001")
        >>> session.start()
    """

    def __init__(
        self,
        session_id: str,
        name: str,
        observer: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an ObservationSession.

        Args:
            session_id: Session ID
            name: Session name
            observer: Observer ID
            metadata: Session metadata

        Example:
            >>> session = ObservationSession("session_001", "Experiment 1", "observer_001")
        """
        if not session_id:
            raise ObservationError("Session ID cannot be empty", {"session_id": session_id})

        if not name:
            raise ObservationError("Session name cannot be empty", {"name": name})

        if not observer:
            raise ObservationError("Observer cannot be empty", {"observer": observer})

        self._id = session_id
        self._name = name
        self._observer = observer
        self._start_time: datetime | None = None
        self._end_time: datetime | None = None
        self._observation_ids: list[str] = []
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the session ID.

        Returns:
            Session ID

        Example:
            >>> sid = session.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the session name.

        Returns:
            Session name

        Example:
            >>> name = session.name
        """
        return self._name

    @property
    def observer(self) -> str:
        """Get the observer ID.

        Returns:
            Observer ID

        Example:
            >>> observer = session.observer
        """
        return self._observer

    @property
    def start_time(self) -> datetime | None:
        """Get the start timestamp.

        Returns:
            Start timestamp

        Example:
            >>> start = session.start_time
        """
        return self._start_time

    @property
    def end_time(self) -> datetime | None:
        """Get the end timestamp.

        Returns:
            End timestamp

        Example:
            >>> end = session.end_time
        """
        return self._end_time

    @property
    def observation_ids(self) -> list[str]:
        """Get the observation IDs.

        Returns:
            Observation IDs

        Example:
            >>> obs_ids = session.observation_ids
        """
        return self._observation_ids.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the session metadata.

        Returns:
            Session metadata

        Example:
            >>> metadata = session.metadata
        """
        return self._metadata.copy()

    def start(self) -> None:
        """Start the observation session.

        Example:
            >>> session.start()
        """
        self._start_time = datetime.now(UTC).replace(tzinfo=None)

    def end(self) -> None:
        """End the observation session.

        Example:
            >>> session.end()
        """
        self._end_time = datetime.now(UTC).replace(tzinfo=None)

    def add_observation(self, observation_id: str) -> None:
        """Add an observation to the session.

        Args:
            observation_id: Observation ID

        Example:
            >>> session.add_observation("obs_001")
        """
        self._observation_ids.append(observation_id)

    def remove_observation(self, observation_id: str) -> bool:
        """Remove an observation from the session.

        Args:
            observation_id: Observation ID

        Returns:
            True if removed

        Example:
            >>> removed = session.remove_observation("obs_001")
        """
        if observation_id in self._observation_ids:
            self._observation_ids.remove(observation_id)
            return True
        return False

    def get_duration(self) -> float | None:
        """Get the session duration in seconds.

        Returns:
            Duration in seconds or None

        Example:
            >>> duration = session.get_duration()
        """
        if self._start_time and self._end_time:
            return (self._end_time - self._start_time).total_seconds()
        return None

    def is_active(self) -> bool:
        """Check if the session is active.

        Returns:
            True if active

        Example:
            >>> active = session.is_active()
        """
        return self._start_time is not None and self._end_time is None

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the session.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> session.add_metadata("location", "lab")
        """
        self._metadata[key] = value

    def validate(self) -> ValidationResult:
        """Validate the session.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = session.validate()
        """
        errors = []

        if not self._id:
            errors.append("Session ID cannot be empty")

        if not self._name:
            errors.append("Session name cannot be empty")

        if self._start_time and self._end_time and self._end_time < self._start_time:
            errors.append("End time cannot be before start time")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Session definition

        Example:
            >>> data = session.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "observer": self._observer,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "end_time": self._end_time.isoformat() if self._end_time else None,
            "duration": self.get_duration(),
            "observation_count": len(self._observation_ids),
            "observation_ids": self._observation_ids,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(session)
        """
        return f"ObservationSession(id={self._id}, name={self._name}, active={self.is_active()}, observations={len(self._observation_ids)})"


# Export
__all__ = [
    "ObservationSession",
]
