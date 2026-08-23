"""
Observation Store Module

This module provides observation store definitions for the Knowledge package.

Purpose
-------
Provide observation store management for storing and retrieving observations.

Responsibilities
----------------
- Define observation store structure
- Support observation store operations
- Support observation store validation
- Support observation store metadata

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.knowledge.exceptions import ObservationError
from quantsmind.knowledge.types import ValidationResult


class ObservationStore:
    """Concrete implementation of an observation store.

    This class provides observation store functionality for managing observations.

    Attributes:
        _id: Store ID
        _observations: Stored observations
        _sessions: Observation sessions
        _metadata: Store metadata

    Example:
        >>> store = ObservationStore("store_001")
        >>> store.add_observation(observation)
    """

    def __init__(
        self,
        store_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an ObservationStore.

        Args:
            store_id: Store ID
            metadata: Store metadata

        Example:
            >>> store = ObservationStore("store_001")
        """
        if not store_id:
            raise ObservationError("Store ID cannot be empty", {"store_id": store_id})

        self._id = store_id
        self._observations: dict[str, Any] = {}
        self._sessions: dict[str, Any] = {}
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the store ID.

        Returns:
            Store ID

        Example:
            >>> sid = store.id
        """
        return self._id

    @property
    def observations(self) -> dict[str, Any]:
        """Get the observations.

        Returns:
            Observations dictionary

        Example:
            >>> observations = store.observations
        """
        return self._observations.copy()

    @property
    def sessions(self) -> dict[str, Any]:
        """Get the sessions.

        Returns:
            Sessions dictionary

        Example:
            >>> sessions = store.sessions
        """
        return self._sessions.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the store metadata.

        Returns:
            Store metadata

        Example:
            >>> metadata = store.metadata
        """
        return self._metadata.copy()

    def add_observation(self, observation: Any) -> None:
        """Add an observation to the store.

        Args:
            observation: Observation to add

        Example:
            >>> store.add_observation(observation)
        """
        obs_id = getattr(observation, 'id', None)
        if obs_id:
            self._observations[obs_id] = observation

    def remove_observation(self, observation_id: str) -> bool:
        """Remove an observation from the store.

        Args:
            observation_id: Observation ID

        Returns:
            True if removed

        Example:
            >>> removed = store.remove_observation("obs_001")
        """
        if observation_id in self._observations:
            del self._observations[observation_id]
            return True
        return False

    def get_observation(self, observation_id: str) -> Any | None:
        """Get an observation from the store.

        Args:
            observation_id: Observation ID

        Returns:
            Observation or None

        Example:
            >>> observation = store.get_observation("obs_001")
        """
        return self._observations.get(observation_id)

    def get_observations_by_observer(self, observer: str) -> list[Any]:
        """Get observations by observer.

        Args:
            observer: Observer ID

        Returns:
            List of observations

        Example:
            >>> observations = store.get_observations_by_observer("observer_001")
        """
        return [obs for obs in self._observations.values() if getattr(obs, 'observer', None) == observer]

    def get_observations_by_target(self, target: str) -> list[Any]:
        """Get observations by target.

        Args:
            target: Target entity ID

        Returns:
            List of observations

        Example:
            >>> observations = store.get_observations_by_target("entity_001")
        """
        return [obs for obs in self._observations.values() if getattr(obs, 'target', None) == target]

    def add_session(self, session: Any) -> None:
        """Add a session to the store.

        Args:
            session: Session to add

        Example:
            >>> store.add_session(session)
        """
        session_id = getattr(session, 'id', None)
        if session_id:
            self._sessions[session_id] = session

    def remove_session(self, session_id: str) -> bool:
        """Remove a session from the store.

        Args:
            session_id: Session ID

        Returns:
            True if removed

        Example:
            >>> removed = store.remove_session("session_001")
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def get_session(self, session_id: str) -> Any | None:
        """Get a session from the store.

        Args:
            session_id: Session ID

        Returns:
            Session or None

        Example:
            >>> session = store.get_session("session_001")
        """
        return self._sessions.get(session_id)

    def get_sessions_by_observer(self, observer: str) -> list[Any]:
        """Get sessions by observer.

        Args:
            observer: Observer ID

        Returns:
            List of sessions

        Example:
            >>> sessions = store.get_sessions_by_observer("observer_001")
        """
        return [session for session in self._sessions.values() if getattr(session, 'observer', None) == observer]

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the store.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> store.add_metadata("location", "lab")
        """
        self._metadata[key] = value

    def validate(self) -> ValidationResult:
        """Validate the store.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = store.validate()
        """
        errors = []

        if not self._id:
            errors.append("Store ID cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Store definition

        Example:
            >>> data = store.to_dict()
        """
        return {
            "id": self._id,
            "observation_count": len(self._observations),
            "session_count": len(self._sessions),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(store)
        """
        return f"ObservationStore(id={self._id}, observations={len(self._observations)}, sessions={len(self._sessions)})"


# Export
__all__ = [
    "ObservationStore",
]
