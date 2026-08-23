"""
Runtime Utilities Module

This module provides utility functions for the Runtime package.

Purpose
-------
Provide utility functions for the QuantsMind SDK.

Responsibilities
----------------
- Provide helper functions
- Support common operations
- Handle data conversion
- Support formatting

Dependencies
------------
typing (standard library)
logging (standard library)
uuid (standard library)
datetime (standard library)
quantsmind.runtime.types (runtime types)
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from quantsmind.runtime.types import SessionID, TaskID

logger = logging.getLogger(__name__)


def generate_id(prefix: str = "id") -> str:
    """Generate a unique identifier.

    Args:
        prefix: ID prefix

    Returns:
        Unique identifier

    Example:
        >>> id = generate_id("session")
    """
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def generate_session_id() -> SessionID:
    """Generate a session ID.

    Returns:
        Session identifier

    Example:
        >>> session_id = generate_session_id()
    """
    return generate_id("session")


def generate_task_id() -> TaskID:
    """Generate a task ID.

    Returns:
        Task identifier

    Example:
        >>> task_id = generate_task_id()
    """
    return generate_id("task")


def format_timestamp(timestamp: datetime) -> str:
    """Format a timestamp.

    Args:
        timestamp: Timestamp to format

    Returns:
        Formatted timestamp string

    Example:
        >>> formatted = format_timestamp(datetime.utcnow())
    """
    return timestamp.isoformat()


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse a timestamp string.

    Args:
        timestamp_str: Timestamp string

    Returns:
        Parsed timestamp

    Example:
        >>> timestamp = parse_timestamp("2024-01-01T00:00:00")
    """
    return datetime.fromisoformat(timestamp_str)


def merge_dicts(*dicts: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple dictionaries.

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary

    Example:
        >>> merged = merge_dicts({"a": 1}, {"b": 2})
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def flatten_dict(d: dict[str, Any], parent_key: str = "", sep: str = ".") -> dict[str, Any]:
    """Flatten a nested dictionary.

    Args:
        d: Dictionary to flatten
        parent_key: Parent key
        sep: Separator

    Returns:
        Flattened dictionary

    Example:
        >>> flat = flatten_dict({"a": {"b": 1}})
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def safe_cast(value: Any, target_type: type, default: Any = None) -> Any:
    """Safely cast a value to a target type.

    Args:
        value: Value to cast
        target_type: Target type
        default: Default value if cast fails

    Returns:
            Casted value or default

    Example:
        >>> value = safe_cast("123", int)
    """
    try:
        return target_type(value)
    except (ValueError, TypeError):
        return default


def validate_required_fields(data: dict[str, Any], required_fields: list[str]) -> list[str]:
    """Validate required fields in data.

    Args:
        data: Data to validate
        required_fields: Required field names

    Returns:
        List of missing fields

    Example:
        >>> missing = validate_required_fields({"a": 1}, ["a", "b"])
    """
    return [field for field in required_fields if field not in data]


def sanitize_string(s: str, max_length: int = 100) -> str:
    """Sanitize a string.

    Args:
        s: String to sanitize
        max_length: Maximum length

    Returns:
        Sanitized string

    Example:
        >>> sanitized = sanitize_string("hello world")
    """
    return s[:max_length].strip()


def truncate_list(lst: list[Any], max_length: int) -> list[Any]:
    """Truncate a list to maximum length.

    Args:
        lst: List to truncate
        max_length: Maximum length

    Returns:
        Truncated list

    Example:
        >>> truncated = truncate_list([1, 2, 3, 4, 5], 3)
    """
    return lst[:max_length]


def deep_copy_dict(d: dict[str, Any]) -> dict[str, Any]:
    """Deep copy a dictionary.

    Args:
        d: Dictionary to copy

    Returns:
        Copied dictionary

    Example:
        >>> copied = deep_copy_dict({"a": 1})
    """
    return {k: v for k, v in d.items()}


# Export
__all__ = [
    "generate_id",
    "generate_session_id",
    "generate_task_id",
    "format_timestamp",
    "parse_timestamp",
    "merge_dicts",
    "flatten_dict",
    "safe_cast",
    "validate_required_fields",
    "sanitize_string",
    "truncate_list",
    "deep_copy_dict",
]
