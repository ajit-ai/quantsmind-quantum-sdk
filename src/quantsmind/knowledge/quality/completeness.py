"""
Completeness Module

This module provides completeness definitions for the Knowledge package.

Purpose
-------
Provide completeness checks for data quality.

Responsibilities
----------------
- Define completeness structure
- Support completeness operations
- Support completeness validation
- Support completeness metadata

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


class Completeness:
    """Concrete implementation of a completeness check.

    This class provides completeness functionality for checking data completeness.

    Attributes:
        _id: Check ID
        _required_fields: Required fields
        _optional_fields: Optional fields
        _metadata: Check metadata

    Example:
        >>> completeness = Completeness("comp_001", ["name", "value"])
        >>> completeness.check({"name": "test", "value": 42})
    """

    def __init__(
        self,
        check_id: str,
        required_fields: List[str],
        optional_fields: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Completeness.

        Args:
            check_id: Check ID
            required_fields: Required field names
            optional_fields: Optional field names
            metadata: Check metadata

        Example:
            >>> completeness = Completeness("comp_001", ["name", "value"])
        """
        if not check_id:
            raise QualityError("Check ID cannot be empty", {"check_id": check_id})

        if not required_fields:
            raise QualityError("Required fields cannot be empty", {"required_fields": required_fields})

        self._id = check_id
        self._required_fields = required_fields
        self._optional_fields = optional_fields or []
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the check ID.

        Returns:
            Check ID

        Example:
            >>> cid = completeness.id
        """
        return self._id

    @property
    def required_fields(self) -> List[str]:
        """Get the required fields.

        Returns:
            Required field names

        Example:
            >>> fields = completeness.required_fields
        """
        return self._required_fields.copy()

    @property
    def optional_fields(self) -> List[str]:
        """Get the optional fields.

        Returns:
            Optional field names

        Example:
            >>> fields = completeness.optional_fields
        """
        return self._optional_fields.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the check metadata.

        Returns:
            Check metadata

        Example:
            >>> metadata = completeness.metadata
        """
        return self._metadata.copy()

    def add_required_field(self, field: str) -> None:
        """Add a required field.

        Args:
            field: Field name

        Example:
            >>> completeness.add_required_field("email")
        """
        if field not in self._required_fields:
            self._required_fields.append(field)

    def remove_required_field(self, field: str) -> bool:
        """Remove a required field.

        Args:
            field: Field name

        Returns:
            True if removed

        Example:
            >>> removed = completeness.remove_required_field("email")
        """
        if field in self._required_fields:
            self._required_fields.remove(field)
            return True
        return False

    def add_optional_field(self, field: str) -> None:
        """Add an optional field.

        Args:
            field: Field name

        Example:
            >>> completeness.add_optional_field("phone")
        """
        if field not in self._optional_fields:
            self._optional_fields.append(field)

    def check(self, data: Dict[str, Any]) -> ValidationResult:
        """Check data completeness.

        Args:
            data: Data to check

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = completeness.check({"name": "test", "value": 42})
        """
        errors = []

        for field in self._required_fields:
            if field not in data:
                errors.append(f"Required field '{field}' is missing")
            elif data[field] is None or data[field] == "":
                errors.append(f"Required field '{field}' is empty")

        return (len(errors) == 0, errors)

    def get_completeness_score(self, data: Dict[str, Any]) -> float:
        """Get completeness score.

        Args:
            data: Data to check

        Returns:
            Completeness score (0.0 to 1.0)

        Example:
            >>> score = completeness.get_completeness_score({"name": "test", "value": 42})
        """
        all_fields = self._required_fields + self._optional_fields
        if not all_fields:
            return 1.0

        filled_count = 0
        for field in all_fields:
            if field in data and data[field] is not None and data[field] != "":
                filled_count += 1

        return filled_count / len(all_fields)

    def validate(self) -> ValidationResult:
        """Validate the completeness check.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = completeness.validate()
        """
        errors = []

        if not self._id:
            errors.append("Check ID cannot be empty")

        if not self._required_fields:
            errors.append("Required fields cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Check definition

        Example:
            >>> data = completeness.to_dict()
        """
        return {
            "id": self._id,
            "required_fields": self._required_fields,
            "optional_fields": self._optional_fields,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(completeness)
        """
        return f"Completeness(id={self._id}, required={len(self._required_fields)}, optional={len(self._optional_fields)})"


# Export
__all__ = [
    "Completeness",
]
