"""Error taxonomy of the QuantsMind Quantum AI/ML Intelligence layer.

QMQ-10 errors subclass :class:`ValueError` so that existing generic
``except ValueError`` handling in the workflow and formulation layers keeps
working.  :class:`MLValidationError` is the structured validation error
raised by the ML models and the formulation adapter.
"""

from __future__ import annotations

__all__ = ["MLError", "MLValidationError"]


class MLError(ValueError):
    """Base error of the QuantsMind Quantum AI/ML Intelligence layer."""


class MLValidationError(MLError):
    """Raised when an ML model or problem fails domain validation."""
