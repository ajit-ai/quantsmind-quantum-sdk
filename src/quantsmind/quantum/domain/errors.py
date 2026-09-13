"""Domain intelligence error hierarchy (QMQ-11).

Cross-domain problems are validated, assessed, planned and dispatched through
the registered domain bindings.  Errors raised while doing so form a small,
backend-agnostic hierarchy derived from :class:`ValueError`.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "DomainError",
    "DomainValidationError",
    "DomainDispatchError",
    "UnsupportedDomainError",
]


class DomainError(ValueError):
    """Base error of the quantum domain intelligence layer."""

    def __init__(
        self,
        message: str,
        *,
        problem: Any = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.problem = problem
        self.details = dict(details or {})


class DomainValidationError(DomainError):
    """Raised when a domain problem fails its own validation rules."""


class DomainDispatchError(DomainError):
    """Raised when a problem cannot be dispatched to a registered domain."""


class UnsupportedDomainError(DomainDispatchError):
    """Raised when no registered domain binding matches a problem."""
