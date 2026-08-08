"""
Freshness Module

This module provides freshness definitions for the Knowledge package.

Purpose
-------
Provide freshness checks for data quality.

Responsibilities
----------------
- Define freshness structure
- Support freshness operations
- Support freshness validation
- Support freshness metadata

Dependencies
------------
typing (standard library)
datetime (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from quantsmind.knowledge.enums import QualityType
from quantsmind.knowledge.exceptions import QualityError
from quantsmind.knowledge.types import ValidationResult


class Freshness:
    """Concrete implementation of a freshness check.

    This class provides freshness functionality for checking data freshness.

    Attributes:
        _id: Check ID
        _max_age: Maximum allowed age in seconds
        _timestamp_field: Field containing timestamp
        _metadata: Check metadata

    Example:
        >>> freshness = Freshness("fresh_001", 86400, "timestamp")
        >>> freshness.check({"timestamp": "2024-01-01T00:00:00"})
    """

    def __init__(
        self,
        check_id: str,
        max_age: int,
        timestamp_field: str = "timestamp",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Freshness.

        Args:
            check_id: Check ID
            max_age: Maximum allowed age in seconds
            timestamp_field: Field containing timestamp
            metadata: Check metadata

        Example:
            >>> freshness = Freshness("fresh_001", 86400, "timestamp")
        """
        if not check_id:
            raise QualityError("Check ID cannot be empty", {"check_id": check_id})

        if max_age < 0:
            raise QualityError("Max age cannot be negative", {"max_age": max_age})

        self._id = check_id
        self._max_age = max_age
        self._timestamp_field = timestamp_field
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the check ID.

        Returns:
            Check ID

        Example:
            >>> fid = freshness.id
        """
        return self._id

    @property
    def max_age(self) -> int:
        """Get the maximum allowed age.

        Returns:
            Maximum age in seconds

        Example:
            >>> max_age = freshness.max_age
        """
        return self._max_age

    @property
    def timestamp_field(self) -> str:
        """Get the timestamp field name.

        Returns:
            Timestamp field name

        Example:
            >>> field = freshness.timestamp_field
        """
        return self._timestamp_field

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the check metadata.

        Returns:
            Check metadata

        Example:
            >>> metadata = freshness.metadata
        """
        return self._metadata.copy()

    def set_max_age(self, max_age: int) -> None:
        """Set the maximum allowed age.

        Args:
            max_age: Maximum age in seconds

        Example:
            >>> freshness.set_max_age(3600)
        """
        if max_age < 0:
            raise QualityError("Max age cannot be negative", {"max_age": max_age})
        self._max_age = max_age

    def set_timestamp_field(self, field: str) -> None:
        """Set the timestamp field.

        Args:
            field: Field name

        Example:
            >>> freshness.set_timestamp_field("created_at")
        """
        self._timestamp_field = field

    def check(self, data: Dict[str, Any]) -> ValidationResult:
        """Check data freshness.

        Args:
            data: Data to check

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = freshness.check({"timestamp": "2024-01-01T00:00:00"})
        """
        errors = []

        if self._timestamp_field not in data:
            errors.append(f"Timestamp field '{self._timestamp_field}' not found")
            return (False, errors)

        timestamp_value = data[self._timestamp_field]

        # Parse timestamp
        try:
            if isinstance(timestamp_value, str):
                timestamp = datetime.fromisoformat(timestamp_value.replace('Z', '+00:00'))
            elif isinstance(timestamp_value, datetime):
                timestamp = timestamp_value
            else:
                errors.append(f"Invalid timestamp format in field '{self._timestamp_field}'")
                return (False, errors)
        except Exception as e:
            errors.append(f"Failed to parse timestamp: {str(e)}")
            return (False, errors)

        # Check age
        age = (datetime.utcnow() - timestamp).total_seconds()
        if age > self._max_age:
            errors.append(f"Data is too old: {age} seconds (max: {self._max_age})")

        return (len(errors) == 0, errors)

    def get_age(self, data: Dict[str, Any]) -> Optional[float]:
        """Get the age of the data.

        Args:
            data: Data to check

        Returns:
            Age in seconds or None

        Example:
            >>> age = freshness.get_age({"timestamp": "2024-01-01T00:00:00"})
        """
        if self._timestamp_field not in data:
            return None

        timestamp_value = data[self._timestamp_field]

        try:
            if isinstance(timestamp_value, str):
                timestamp = datetime.fromisoformat(timestamp_value.replace('Z', '+00:00'))
            elif isinstance(timestamp_value, datetime):
                timestamp = timestamp_value
            else:
                return None

            return (datetime.utcnow() - timestamp).total_seconds()
        except Exception:
            return None

    def get_freshness_score(self, data: Dict[str, Any]) -> float:
        """Get freshness score.

        Args:
            data: Data to check

        Returns:
            Freshness score (0.0 to 1.0)

        Example:
            >>> score = freshness.get_freshness_score({"timestamp": "2024-01-01T00:00:00"})
        """
        age = self.get_age(data)
        if age is None:
            return 0.0

        if age >= self._max_age:
            return 0.0

        return 1.0 - (age / self._max_age)

    def validate(self) -> ValidationResult:
        """Validate the freshness check.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = freshness.validate()
        """
        errors = []

        if not self._id:
            errors.append("Check ID cannot be empty")

        if self._max_age < 0:
            errors.append("Max age cannot be negative")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Check definition

        Example:
            >>> data = freshness.to_dict()
        """
        return {
            "id": self._id,
            "max_age": self._max_age,
            "timestamp_field": self._timestamp_field,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(freshness)
        """
        return f"Freshness(id={self._id}, max_age={self._max_age}s, field={self._timestamp_field})"


# Export
__all__ = [
    "Freshness",
]
