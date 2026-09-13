"""Typed execution errors for QuantsMind Quantum (QMQ-04).

The failure taxonomy is explicit: callers can distinguish a missing
MicroQuantum dependency from a failed quantum run, a bad decoded result,
an unsupported strategy, or a classical execution failure — without
swallowing any of them.
"""

from __future__ import annotations


class ExecutionError(ValueError):
    """Base class for execution-layer failures."""


class WorkflowError(ValueError):
    """Raised when a workflow step cannot proceed.

    Kept in this module (rather than the workflow package) so dependency
    errors can subclass it without creating an import cycle.
    """


class MicroQuantumUnavailableError(ImportError, WorkflowError):
    """MicroQuantum is not importable but a quantum strategy needed it.

    Subclasses both :class:`ImportError` (so ``except ImportError`` catches
    it at the engine boundary) and :class:`WorkflowError` (so workflow-level
    callers keep their existing behaviour).
    """


class ClassicalExecutionError(ExecutionError):
    """The classical baseline could not execute the plan."""


class QuantumExecutionError(ExecutionError):
    """A quantum execution failed while delegating to MicroQuantum."""


class HybridExecutionError(ExecutionError):
    """A hybrid execution failed because no leg produced a result."""


class InvalidQuantumResultError(ExecutionError):
    """A decoded quantum result failed validation (variables/values/energy)."""


class UnsupportedStrategyError(ExecutionError):
    """The requested strategy/executor combination is not supported."""


class InvalidExecutionOptionError(ExecutionError):
    """An execution option is invalid for the requested strategy."""


__all__ = [
    "ExecutionError",
    "WorkflowError",
    "MicroQuantumUnavailableError",
    "ClassicalExecutionError",
    "QuantumExecutionError",
    "HybridExecutionError",
    "InvalidQuantumResultError",
    "UnsupportedStrategyError",
    "InvalidExecutionOptionError",
]
