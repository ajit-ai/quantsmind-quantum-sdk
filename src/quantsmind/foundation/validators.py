"""
Validators Module

This module provides common validation utilities for the Foundation package.
Validators provide reusable validation logic for foundation objects.

Purpose
-------
Provide common validation utilities for the Foundation package.

Scientific Meaning
------------------
Validators ensure data integrity and correctness in scientific computing applications,
preventing invalid states and ensuring consistent behavior.

Responsibilities
----------------
- Provide common validation functions
- Support type validation
- Enable range validation
- Support custom validators

Dependencies
------------
typing (standard library)
quantsmind.foundation.exceptions (exception hierarchy)
quantsmind.foundation.types (type definitions)

Future Extensions
-----------------
- Async validators
- Composite validators
- Validator composition
- Validator caching
"""

from __future__ import annotations

import logging
from typing import Any, Callable, List, Optional, Tuple

from quantsmind.foundation.exceptions import ValidationError
from quantsmind.foundation.types import ValidationResult

logger = logging.getLogger(__name__)


def validate_type(value: Any, expected_type: type) -> ValidationResult:
    """Validate that a value is of the expected type.

    Args:
        value: Value to validate
        expected_type: Expected type

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_type(42, int)
    """
    if isinstance(value, expected_type):
        return (True, [])
    return (False, [f"Expected type {expected_type.__name__}, got {type(value).__name__}"])


def validate_range(value: float, min_val: Optional[float] = None, max_val: Optional[float] = None) -> ValidationResult:
    """Validate that a value is within a range.

    Args:
        value: Value to validate
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_range(5.0, min_val=0.0, max_val=10.0)
    """
    errors: List[str] = []

    if min_val is not None and value < min_val:
        errors.append(f"Value {value} is below minimum {min_val}")

    if max_val is not None and value > max_val:
        errors.append(f"Value {value} is above maximum {max_val}")

    return (len(errors) == 0, errors)


def validate_string_length(value: str, min_len: Optional[int] = None, max_len: Optional[int] = None) -> ValidationResult:
    """Validate that a string length is within a range.

    Args:
        value: String to validate
        min_len: Minimum length (inclusive)
        max_len: Maximum length (inclusive)

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_string_length("hello", min_len=1, max_len=10)
    """
    errors: List[str] = []

    if min_len is not None and len(value) < min_len:
        errors.append(f"String length {len(value)} is below minimum {min_len}")

    if max_len is not None and len(value) > max_len:
        errors.append(f"String length {len(value)} is above maximum {max_len}")

    return (len(errors) == 0, errors)


def validate_not_none(value: Any) -> ValidationResult:
    """Validate that a value is not None.

    Args:
        value: Value to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_not_none(42)
    """
    if value is not None:
        return (True, [])
    return (False, ["Value cannot be None"])


def validate_positive(value: float) -> ValidationResult:
    """Validate that a value is positive.

    Args:
        value: Value to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_positive(5.0)
    """
    if value > 0:
        return (True, [])
    return (False, [f"Value {value} must be positive"])


def validate_non_negative(value: float) -> ValidationResult:
    """Validate that a value is non-negative.

    Args:
        value: Value to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_non_negative(5.0)
    """
    if value >= 0:
        return (True, [])
    return (False, [f"Value {value} must be non-negative"])


def validate_custom(value: Any, validator: Callable[[Any], bool], error_message: str) -> ValidationResult:
    """Validate a value using a custom validator function.

    Args:
        value: Value to validate
        validator: Custom validator function (returns bool)
        error_message: Error message if validation fails

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> def is_even(x): return x % 2 == 0
        >>> is_valid, errors = validate_custom(4, is_even, "Value must be even")
    """
    if validator(value):
        return (True, [])
    return (False, [error_message])


def validate_all(value: Any, validators: List[Callable[[Any], ValidationResult]]) -> ValidationResult:
    """Validate a value using multiple validators.

    Args:
        value: Value to validate
        validators: List of validator functions

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> validators = [lambda x: validate_type(x, int), lambda x: validate_positive(x)]
        >>> is_valid, errors = validate_all(5, validators)
    """
    all_errors: List[str] = []

    for validator in validators:
        is_valid, errors = validator(value)
        if not is_valid:
            all_errors.extend(errors)

    return (len(all_errors) == 0, all_errors)


class Validator:
    """Base class for custom validators.

    This class provides a framework for creating reusable validators
    with pre-conditions and post-conditions.

    Example:
        >>> class PositiveValidator(Validator):
        ...     def validate(self, value: Any) -> ValidationResult:
        ...         return validate_positive(value)
    """

    def validate(self, value: Any) -> ValidationResult:
        """Validate a value.

        Args:
            value: Value to validate

        Returns:
            Tuple of (is_valid, error_messages)

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement validate method")

    def __call__(self, value: Any) -> ValidationResult:
        """Make the validator callable.

        Args:
            value: Value to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        return self.validate(value)


# Export
__all__ = [
    "validate_type",
    "validate_range",
    "validate_string_length",
    "validate_not_none",
    "validate_positive",
    "validate_non_negative",
    "validate_custom",
    "validate_all",
    "Validator",
]
