"""
Helpers Module

This module provides helper functions for the QuantsMind SDK.

Purpose
-------
Provide common utility functions used across the SDK.

Functions
-------
- validate_type: Type validation
- clamp: Clamp value to range
- safe_division: Safe division with zero check
- format_number: Format number for display

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

from typing import Any, List, Optional, Type, TypeVar
import math


T = TypeVar("T")


def validate_type(value: Any, expected_type: Type[T], name: str = "value") -> T:
    """Validate that a value is of the expected type.

    Args:
        value: Value to validate
        expected_type: Expected type
        name: Name of the value (for error messages)

    Returns:
        The value if type matches

    Raises:
        TypeError: If type doesn't match

    Example:
        >>> result = validate_type(1.0, float, "param")
    """
    if not isinstance(value, expected_type):
        raise TypeError(f"{name} must be of type {expected_type.__name__}, got {type(value).__name__}")
    return value


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value to a range.

    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Clamped value

    Example:
        >>> result = clamp(5.0, 0.0, 10.0)
    """
    return max(min_val, min(max_val, value))


def safe_division(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Perform safe division with zero check.

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if denominator is zero

    Returns:
        Division result or default

    Example:
        >>> result = safe_division(10.0, 0.0, default=0.0)
    """
    if denominator == 0:
        return default
    return numerator / denominator


def format_number(value: float, precision: int = 6) -> str:
    """Format a number for display.

    Args:
        value: Number to format
        precision: Number of decimal places

    Returns:
        Formatted string

    Example:
        >>> formatted = format_number(3.14159265359, precision=4)
    """
    if math.isinf(value):
        return "inf" if value > 0 else "-inf"
    if math.isnan(value):
        return "nan"
    return f"{value:.{precision}f}"


def is_close(a: float, b: float, rel_tol: float = 1e-9, abs_tol: float = 0.0) -> bool:
    """Check if two numbers are close.

    Args:
        a: First number
        b: Second number
        rel_tol: Relative tolerance
        abs_tol: Absolute tolerance

    Returns:
        True if numbers are close

    Example:
        >>> close = is_close(1.0, 1.0000001)
    """
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """Split a list into chunks.

    Args:
        lst: List to split
        chunk_size: Size of each chunk

    Returns:
        List of chunks

    Example:
        >>> chunks = chunk_list([1, 2, 3, 4, 5], 2)
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_list(nested: List[List[T]]) -> List[T]:
    """Flatten a nested list.

    Args:
        nested: Nested list

    Returns:
        Flattened list

    Example:
        >>> flat = flatten_list([[1, 2], [3, 4]])
    """
    return [item for sublist in nested for item in sublist]


def unique_preserve_order(lst: List[T]) -> List[T]:
    """Get unique elements while preserving order.

    Args:
        lst: Input list

    Returns:
        List with unique elements in original order

    Example:
        >>> unique = unique_preserve_order([1, 2, 1, 3, 2])
    """
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


__all__ = [
    "validate_type",
    "clamp",
    "safe_division",
    "format_number",
    "is_close",
    "chunk_list",
    "flatten_list",
    "unique_preserve_order",
]
