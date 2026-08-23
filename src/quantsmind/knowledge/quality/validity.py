"""
Validity Module

This module provides validity definitions for the Knowledge package.

Purpose
-------
Provide validity checks for data quality.

Responsibilities
----------------
- Define validity structure
- Support validity operations
- Support validity validation
- Support validity metadata

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from quantsmind.knowledge.exceptions import QualityError
from quantsmind.knowledge.types import ValidationResult


class Validity:
    """Concrete implementation of a validity check.

    This class provides validity functionality for checking data validity.

    Attributes:
        _id: Check ID
        _field_validators: Field validators
        _metadata: Check metadata

    Example:
        >>> validity = Validity("valid_001")
        >>> validity.add_field_validator("email", lambda x: "@" in x)
    """

    def __init__(
        self,
        check_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Validity.

        Args:
            check_id: Check ID
            metadata: Check metadata

        Example:
            >>> validity = Validity("valid_001")
        """
        if not check_id:
            raise QualityError("Check ID cannot be empty", {"check_id": check_id})

        self._id = check_id
        self._field_validators: dict[str, Callable[[Any], bool]] = {}
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the check ID.

        Returns:
            Check ID

        Example:
            >>> vid = validity.id
        """
        return self._id

    @property
    def field_validators(self) -> dict[str, str]:
        """Get the field validator names.

        Returns:
            Field names

        Example:
            >>> fields = validity.field_validators
        """
        return list(self._field_validators.keys())

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the check metadata.

        Returns:
            Check metadata

        Example:
            >>> metadata = validity.metadata
        """
        return self._metadata.copy()

    def add_field_validator(self, field: str, validator: Callable[[Any], bool]) -> None:
        """Add a field validator.

        Args:
            field: Field name
            validator: Validator function

        Example:
            >>> validity.add_field_validator("email", lambda x: "@" in x)
        """
        self._field_validators[field] = validator

    def remove_field_validator(self, field: str) -> bool:
        """Remove a field validator.

        Args:
            field: Field name

        Returns:
            True if removed

        Example:
            >>> removed = validity.remove_field_validator("email")
        """
        if field in self._field_validators:
            del self._field_validators[field]
            return True
        return False

    def check(self, data: dict[str, Any]) -> ValidationResult:
        """Check data validity.

        Args:
            data: Data to check

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validity.check({"email": "test@example.com"})
        """
        errors = []

        for field, validator in self._field_validators.items():
            if field in data:
                try:
                    if not validator(data[field]):
                        errors.append(f"Field '{field}' is invalid")
                except Exception as e:
                    errors.append(f"Validation error for field '{field}': {str(e)}")

        return (len(errors) == 0, errors)

    def check_field(self, field: str, value: Any) -> ValidationResult:
        """Check a single field value.

        Args:
            field: Field name
            value: Field value

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validity.check_field("email", "test@example.com")
        """
        if field not in self._field_validators:
            return (True, [])

        try:
            result = self._field_validators[field](value)
            return (result, [] if result else [f"Field '{field}' is invalid"])
        except Exception as e:
            return (False, [f"Validation error for field '{field}': {str(e)}"])

    def get_validity_score(self, data: dict[str, Any]) -> float:
        """Get validity score.

        Args:
            data: Data to check

        Returns:
            Validity score (0.0 to 1.0)

        Example:
            >>> score = validity.get_validity_score({"email": "test@example.com"})
        """
        if not self._field_validators:
            return 1.0

        passed_count = 0
        checked_count = 0

        for field, validator in self._field_validators.items():
            if field in data:
                checked_count += 1
                try:
                    if validator(data[field]):
                        passed_count += 1
                except Exception:
                    pass

        if checked_count == 0:
            return 1.0

        return passed_count / checked_count

    def validate(self) -> ValidationResult:
        """Validate the validity check.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validity.validate()
        """
        errors = []

        if not self._id:
            errors.append("Check ID cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Check definition

        Example:
            >>> data = validity.to_dict()
        """
        return {
            "id": self._id,
            "fields": list(self._field_validators.keys()),
            "field_count": len(self._field_validators),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(validity)
        """
        return f"Validity(id={self._id}, fields={len(self._field_validators)})"


# Export
__all__ = [
    "Validity",
]
