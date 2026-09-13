"""Execution layer of QuantsMind Quantum (QMQ-04).

Classical, quantum and hybrid executors turn a :class:`ExecutorContext`
(problem + computation plan + mapped payloads + options) into normalized,
comparable execution results with an explicit failure taxonomy.
"""

from __future__ import annotations

from quantsmind.quantum.execution.classical import (
    ClassicalExecutionResult,
    ClassicalExecutor,
)
from quantsmind.quantum.execution.comparison import (
    ExecutionComparison,
    ExecutionComparisonEntry,
)
from quantsmind.quantum.execution.errors import (
    ClassicalExecutionError,
    ExecutionError,
    HybridExecutionError,
    InvalidExecutionOptionError,
    InvalidQuantumResultError,
    MicroQuantumUnavailableError,
    QuantumExecutionError,
    UnsupportedStrategyError,
    WorkflowError,
)
from quantsmind.quantum.execution.executor import Executor, ExecutorContext
from quantsmind.quantum.execution.hybrid import (
    HybridExecutionResult,
    HybridExecutor,
)
from quantsmind.quantum.execution.options import ExecutionOptions
from quantsmind.quantum.execution.quantum import (
    QuantumExecutionResult,
    QuantumExecutor,
)

__all__ = [
    "Executor",
    "ExecutorContext",
    "ExecutionOptions",
    "ClassicalExecutor",
    "ClassicalExecutionResult",
    "QuantumExecutor",
    "QuantumExecutionResult",
    "HybridExecutor",
    "HybridExecutionResult",
    "ExecutionComparison",
    "ExecutionComparisonEntry",
    "ExecutionError",
    "ClassicalExecutionError",
    "QuantumExecutionError",
    "HybridExecutionError",
    "InvalidQuantumResultError",
    "MicroQuantumUnavailableError",
    "UnsupportedStrategyError",
    "InvalidExecutionOptionError",
    "WorkflowError",
]
