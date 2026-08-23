"""
Observation Record Module

This module provides observation record definitions for the Knowledge package.

Purpose
-------
Provide observation record management for observation tracking.

Responsibilities
----------------
- Define observation record structure
- Support observation record operations
- Support observation record validation
- Support observation record metadata

Dependencies
------------
typing (standard library)
datetime (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from quantsmind.knowledge.exceptions import ObservationError
from quantsmind.knowledge.types import ValidationResult


class ObservationRecord:
    """Concrete implementation of an observation record.

    This class provides observation record functionality.

    Attributes:
        _id: Record ID
        _observation_id: Observation ID
        _timestamp: Record timestamp
        _data: Record data
        _status: Record status
        _metadata: Record metadata

    Example:
        >>> record = ObservationRecord("record_001", "obs_001")
        >>> record.add_data({"value": 42})
    """

    def __init__(
        self,
        record_id: str,
        observation_id: str,
        data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an ObservationRecord.

        Args:
            record_id: Record ID
            observation_id: Observation ID
            data: Record data
            metadata: Record metadata

        Example:
            >>> record = ObservationRecord("record_001", "obs_001")
        """
        if not record_id:
            raise ObservationError("Record ID cannot be empty", {"record_id": record_id})

        if not observation_id:
            raise ObservationError("Observation ID cannot be empty", {"observation_id": observation_id})

        self._id = record_id
        self._observation_id = observation_id
        self._timestamp = datetime.utcnow()
        self._data = data or {}
        self._status = "pending"
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the record ID.

        Returns:
            Record ID

        Example:
            >>> rid = record.id
        """
        return self._id

    @property
    def observation_id(self) -> str:
        """Get the observation ID.

        Returns:
            Observation ID

        Example:
            >>> obs_id = record.observation_id
        """
        return self._observation_id

    @property
    def timestamp(self) -> datetime:
        """Get the record timestamp.

        Returns:
            Timestamp

        Example:
            >>> timestamp = record.timestamp
        """
        return self._timestamp

    @property
    def data(self) -> dict[str, Any]:
        """Get the record data.

        Returns:
            Record data

        Example:
            >>> data = record.data
        """
        return self._data.copy()

    @property
    def status(self) -> str:
        """Get the record status.

        Returns:
            Record status

        Example:
            >>> status = record.status
        """
        return self._status

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the record metadata.

        Returns:
            Record metadata

        Example:
            >>> metadata = record.metadata
        """
        return self._metadata.copy()

    def add_data(self, key: str, value: Any) -> None:
        """Add data to the record.

        Args:
            key: Data key
            value: Data value

        Example:
            >>> record.add_data("value", 42)
        """
        self._data[key] = value

    def set_status(self, status: str) -> None:
        """Set the record status.

        Args:
            status: Record status

        Example:
            >>> record.set_status("completed")
        """
        self._status = status

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the record.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> record.add_metadata("location", "lab")
        """
        self._metadata[key] = value

    def validate(self) -> ValidationResult:
        """Validate the record.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = record.validate()
        """
        errors = []

        if not self._id:
            errors.append("Record ID cannot be empty")

        if not self._observation_id:
            errors.append("Observation ID cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Record definition

        Example:
            >>> data = record.to_dict()
        """
        return {
            "id": self._id,
            "observation_id": self._observation_id,
            "timestamp": self._timestamp.isoformat(),
            "data": self._data,
            "status": self._status,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(record)
        """
        return f"ObservationRecord(id={self._id}, observation_id={self._observation_id}, status={self._status})"


# Export
__all__ = [
    "ObservationRecord",
]
