"""
Observation Module

This module provides observation definitions for the Knowledge package.

Purpose
-------
Provide observation management and tracking.

Responsibilities
----------------
- Define observation structure
- Support observation operations
- Support observation validation
- Support observation metadata

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
from quantsmind.knowledge.types import (
    ObservationData,
    ObservationID,
    ValidationResult,
)


class Observation:
    """Concrete implementation of an observation.

    This class provides observation functionality.

    Attributes:
        _id: Observation ID
        _timestamp: Observation timestamp
        _observer: Observer ID
        _target: Target entity ID
        _data: Observation data
        _metadata: Observation metadata

    Example:
        >>> observation = Observation("obs_001", "observer_001", "entity_001")
        >>> observation.add_data({"value": 42})
    """

    def __init__(
        self,
        observation_id: ObservationID,
        observer: str,
        target: str,
        data: ObservationData | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an Observation.

        Args:
            observation_id: Observation ID
            observer: Observer ID
            target: Target entity ID
            data: Observation data
            metadata: Observation metadata

        Example:
            >>> observation = Observation("obs_001", "observer_001", "entity_001")
        """
        if not observation_id:
            raise ObservationError("Observation ID cannot be empty", {"observation_id": observation_id})

        if not observer:
            raise ObservationError("Observer cannot be empty", {"observer": observer})

        if not target:
            raise ObservationError("Target cannot be empty", {"target": target})

        self._id = observation_id
        self._timestamp = datetime.now(UTC).replace(tzinfo=None)
        self._observer = observer
        self._target = target
        self._data = data or {}
        self._metadata = metadata or {}

    @property
    def id(self) -> ObservationID:
        """Get the observation ID.

        Returns:
            Observation ID

        Example:
            >>> oid = observation.id
        """
        return self._id

    @property
    def timestamp(self) -> datetime:
        """Get the observation timestamp.

        Returns:
            Timestamp

        Example:
            >>> timestamp = observation.timestamp
        """
        return self._timestamp

    @property
    def observer(self) -> str:
        """Get the observer ID.

        Returns:
            Observer ID

        Example:
            >>> observer = observation.observer
        """
        return self._observer

    @property
    def target(self) -> str:
        """Get the target entity ID.

        Returns:
            Target entity ID

        Example:
            >>> target = observation.target
        """
        return self._target

    @property
    def data(self) -> ObservationData:
        """Get the observation data.

        Returns:
            Observation data

        Example:
            >>> data = observation.data
        """
        return self._data.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the observation metadata.

        Returns:
            Observation metadata

        Example:
            >>> metadata = observation.metadata
        """
        return self._metadata.copy()

    def add_data(self, key: str, value: Any) -> None:
        """Add data to the observation.

        Args:
            key: Data key
            value: Data value

        Example:
            >>> observation.add_data("value", 42)
        """
        self._data[key] = value

    def remove_data(self, key: str) -> bool:
        """Remove data from the observation.

        Args:
            key: Data key

        Returns:
            True if removed

        Example:
            >>> removed = observation.remove_data("value")
        """
        if key in self._data:
            del self._data[key]
            return True
        return False

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the observation.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> observation.add_metadata("location", "lab")
        """
        self._metadata[key] = value

    def validate(self) -> ValidationResult:
        """Validate the observation.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = observation.validate()
        """
        errors = []

        if not self._id:
            errors.append("Observation ID cannot be empty")

        if not self._observer:
            errors.append("Observer cannot be empty")

        if not self._target:
            errors.append("Target cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Observation definition

        Example:
            >>> data = observation.to_dict()
        """
        return {
            "id": self._id,
            "timestamp": self._timestamp.isoformat(),
            "observer": self._observer,
            "target": self._target,
            "data": self._data,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(observation)
        """
        return f"Observation(id={self._id}, observer={self._observer}, target={self._target}, timestamp={self._timestamp.isoformat()})"


# Export
__all__ = [
    "Observation",
]
