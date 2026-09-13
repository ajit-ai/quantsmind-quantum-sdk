"""Error taxonomy of the QuantsMind Quantum Data Intelligence layer.

QMQ-09 errors subclass :class:`ValueError` so that existing generic
``except ValueError`` handling in the workflow and formulation layers keeps
working.  :class:`DataValidationError` is the structured validation error
raised by the Data models and the formulation adapter.
"""

from __future__ import annotations

__all__ = ["DataError", "DataValidationError"]


class DataError(ValueError):
    """Base error of the QuantsMind Quantum Data Intelligence layer."""


class DataValidationError(DataError):
    """Raised when a Data model or problem fails domain validation."""
