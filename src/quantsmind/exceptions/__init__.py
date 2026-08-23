"""
Exceptions Package — Defines the SDK-wide exception hierarchy so every package raises
consistent, catchable, well-documented errors.

This package is part of the QuantsMind SDK (R0.1.0).
R0.2.0: the SDK base exception is now implemented; package-level hierarchies
inherit from :class:`QuantsMindError`.
"""

from __future__ import annotations

from typing import Any


class QuantsMindError(Exception):
    """Base exception for all errors raised by the QuantsMind SDK.

    Every package-level exception hierarchy inherits from this class so
    callers can catch any SDK error with a single ``except QuantsMindError``.

    Attributes:
        message: Human-readable error message.
        details: Optional dictionary with additional error context.
        error_code: Optional machine-readable error code.

    Example:
        >>> try:
        ...     raise QuantsMindError("boom", details={"op": "solve"})
        ... except QuantsMindError as e:
        ...     print(e.message, e.details)
    """

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        error_code: str | None = None,
    ) -> None:
        """Initialize a QuantsMindError.

        Args:
            message: Human-readable error message.
            details: Optional dictionary with additional error context.
            error_code: Optional machine-readable error code.
        """
        super().__init__(message)
        self.message = message
        self.details = details if details is not None else {}
        self.error_code = error_code

    def __str__(self) -> str:
        """Return the message, annotated with the error code when present."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


__all__: list[str] = ["QuantsMindError"]
