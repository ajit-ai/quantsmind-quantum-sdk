"""Structured-output helpers.

Parse model text as JSON and validate required keys. Parsing failures
and missing keys surface as :class:`StructuredOutputError`.
"""

from __future__ import annotations

import json
from typing import Any

__all__ = [
    "StructuredOutputError",
    "parse_json_output",
]


class StructuredOutputError(ValueError):
    """Raised when model output is not the expected JSON object."""


def parse_json_output(text: str, required_keys: list[str] | None = None) -> dict[str, Any]:
    """Parse ``text`` as a JSON object and check required keys.

    Args:
        text: Model output text.
        required_keys: Keys that must be present.

    Raises:
        StructuredOutputError: If parsing fails, the result is not an
            object, or a required key is missing.
    """
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise StructuredOutputError(f"output is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise StructuredOutputError(f"output must be a JSON object, got {type(data).__name__}")
    for key in required_keys or []:
        if key not in data:
            raise StructuredOutputError(f"output missing required key: {key!r}")
    return data
