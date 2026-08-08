"""
Uniqueness Module

This module provides uniqueness definitions for the Knowledge package.

Purpose
-------
Provide uniqueness checks for data quality.

Responsibilities
----------------
- Define uniqueness structure
- Support uniqueness operations
- Support uniqueness validation
- Support uniqueness metadata

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.knowledge.enums import QualityType
from quantsmind.knowledge.exceptions import QualityError
from quantsmind.knowledge.types import ValidationResult


class Uniqueness:
    """Concrete implementation of a uniqueness check.

    This class provides uniqueness functionality for checking data uniqueness.

    Attributes:
        _id: Check ID
        _unique_fields: Fields that must be unique
        _seen_values: Seen values for uniqueness checking
        _metadata: Check metadata

    Example:
        >>> uniqueness = Uniqueness("uniq_001", ["id", "email"])
        >>> uniqueness.check({"id": 1, "email": "test@example.com"})
    """

    def __init__(
        self,
        check_id: str,
        unique_fields: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Uniqueness.

        Args:
            check_id: Check ID
            unique_fields: Fields that must be unique
            metadata: Check metadata

        Example:
            >>> uniqueness = Uniqueness("uniq_001", ["id", "email"])
        """
        if not check_id:
            raise QualityError("Check ID cannot be empty", {"check_id": check_id})

        if not unique_fields:
            raise QualityError("Unique fields cannot be empty", {"unique_fields": unique_fields})

        self._id = check_id
        self._unique_fields = unique_fields
        self._seen_values: Dict[str, set] = {field: set() for field in unique_fields}
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the check ID.

        Returns:
            Check ID

        Example:
            >>> uid = uniqueness.id
        """
        return self._id

    @property
    def unique_fields(self) -> List[str]:
        """Get the unique fields.

        Returns:
            Unique field names

        Example:
            >>> fields = uniqueness.unique_fields
        """
        return self._unique_fields.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the check metadata.

        Returns:
            Check metadata

        Example:
            >>> metadata = uniqueness.metadata
        """
        return self._metadata.copy()

    def add_unique_field(self, field: str) -> None:
        """Add a unique field.

        Args:
            field: Field name

        Example:
            >>> uniqueness.add_unique_field("username")
        """
        if field not in self._unique_fields:
            self._unique_fields.append(field)
            self._seen_values[field] = set()

    def remove_unique_field(self, field: str) -> bool:
        """Remove a unique field.

        Args:
            field: Field name

        Returns:
            True if removed

        Example:
            >>> removed = uniqueness.remove_unique_field("username")
        """
        if field in self._unique_fields:
            self._unique_fields.remove(field)
            del self._seen_values[field]
            return True
        return False

    def check(self, data: Dict[str, Any]) -> ValidationResult:
        """Check data uniqueness.

        Args:
            data: Data to check

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = uniqueness.check({"id": 1, "email": "test@example.com"})
        """
        errors = []

        for field in self._unique_fields:
            if field not in data:
                errors.append(f"Unique field '{field}' not found in data")
                continue

            value = data[field]
            if value in self._seen_values[field]:
                errors.append(f"Duplicate value for field '{field}': {value}")

        return (len(errors) == 0, errors)

    def record(self, data: Dict[str, Any]) -> None:
        """Record data values for future uniqueness checks.

        Args:
            data: Data to record

        Example:
            >>> uniqueness.record({"id": 1, "email": "test@example.com"})
        """
        for field in self._unique_fields:
            if field in data:
                self._seen_values[field].add(data[field])

    def reset(self) -> None:
        """Reset the seen values.

        Example:
            >>> uniqueness.reset()
        """
        self._seen_values = {field: set() for field in self._unique_fields}

    def get_duplicate_count(self, field: str) -> int:
        """Get the count of duplicates for a field.

        Args:
            field: Field name

        Returns:
            Duplicate count

        Example:
            >>> count = uniqueness.get_duplicate_count("email")
        """
        if field not in self._seen_values:
            return 0
        return len(self._seen_values[field])

    def get_uniqueness_score(self, data: Dict[str, Any]) -> float:
        """Get uniqueness score.

        Args:
            data: Data to check

        Returns:
            Uniqueness score (0.0 to 1.0)

        Example:
            >>> score = uniqueness.get_uniqueness_score({"id": 1, "email": "test@example.com"})
        """
        if not self._unique_fields:
            return 1.0

        unique_count = 0
        total_count = 0

        for field in self._unique_fields:
            if field in data:
                total_count += 1
                if data[field] not in self._seen_values[field]:
                    unique_count += 1

        if total_count == 0:
            return 1.0

        return unique_count / total_count

    def validate(self) -> ValidationResult:
        """Validate the uniqueness check.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = uniqueness.validate()
        """
        errors = []

        if not self._id:
            errors.append("Check ID cannot be empty")

        if not self._unique_fields:
            errors.append("Unique fields cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Check definition

        Example:
            >>> data = uniqueness.to_dict()
        """
        return {
            "id": self._id,
            "unique_fields": self._unique_fields,
            "field_count": len(self._unique_fields),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(uniqueness)
        """
        return f"Uniqueness(id={self._id}, fields={self._unique_fields})"


# Export
__all__ = [
    "Uniqueness",
]
