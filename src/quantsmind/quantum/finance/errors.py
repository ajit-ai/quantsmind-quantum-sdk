"""Error taxonomy of the QuantsMind Quantum Finance domain layer.

QMQ-07 errors subclass :class:`ValueError` so that existing generic
``except ValueError`` handling in the workflow and formulation layers keeps
working.  :class:`FinanceValidationError` is the structured validation
error raised by the Finance models and the formulation adapter.
"""

from __future__ import annotations

__all__ = ["FinanceError", "FinanceValidationError"]


class FinanceError(ValueError):
    """Base error of the QuantsMind Quantum Finance domain layer."""


class FinanceValidationError(FinanceError):
    """Raised when a Finance model or problem fails domain validation."""
