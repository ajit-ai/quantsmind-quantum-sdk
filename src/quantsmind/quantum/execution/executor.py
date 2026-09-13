"""Executor abstraction for QuantsMind Quantum (QMQ-04 §2).

An :class:`Executor` turns a :class:`ExecutorContext` (problem + computation
plan + mapped payloads + options) into a normalized execution result through
a predictable, common interface:

``prepare() -> execute() -> validate()``
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from quantsmind.quantum.execution.options import ExecutionOptions
from quantsmind.quantum.strategy.strategy import ComputationStrategy

if TYPE_CHECKING:
    from quantsmind.quantum.intelligence.capabilities import CapabilityModel
    from quantsmind.quantum.strategy.strategy import ComputationStrategy


@dataclass
class ExecutorContext:
    """Everything one executor needs to run one plan.

    Args:
        problem: The domain problem being executed.
        plan: The QMQ-03 computation plan (the plan drives execution).
        formulation: Formulation produced for the problem (optional).
        qubo: Mapped QUBO model (used by the classical leg).
        ising: Mapped Ising model (used by the quantum leg).
        options: Execution configuration for this run.
        metadata: Free-form contextual metadata.
    """

    problem: Any
    plan: Any
    formulation: Any | None = None
    qubo: Any | None = None
    ising: Any | None = None
    options: ExecutionOptions = field(default_factory=ExecutionOptions)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def strategy(self) -> ComputationStrategy | None:
        """Strategy resolving options override, then the plan, then ``None``."""
        if self.options.resolved_strategy is not None:
            return self.options.resolved_strategy
        plan_strategy = getattr(self.plan, "strategy", None)
        return plan_strategy if isinstance(plan_strategy, ComputationStrategy) else None

    @property
    def algorithm(self) -> str | None:
        """Algorithm resolving options override, then the plan."""
        return self.options.algorithm or self.plan.algorithm


class Executor(ABC):
    """Common interface for classical / quantum / hybrid executors.

    Subclasses identify themselves through :attr:`name` and
    :attr:`executor_id` and declare which strategies they implement in
    :attr:`strategies`.  Execution is ``prepare -> execute -> validate``;
    each step may raise the typed :mod:`quantsmind.quantum.execution.errors`.
    """

    name: ClassVar[str] = "executor"
    executor_id: ClassVar[str] = "executor"
    strategies: ClassVar[tuple[ComputationStrategy, ...]] = ()

    def is_available(self, capabilities: CapabilityModel | None = None) -> bool:
        """Whether this executor can currently execute (default: True)."""
        return True

    def prepare(self, context: ExecutorContext) -> None:
        """Validate inputs and fail fast before any real work."""
        return None

    @abstractmethod
    def execute(self, context: ExecutorContext) -> Any:
        """Run the planned computation and return a normalized result."""

    def validate(self, result: Any, context: ExecutorContext) -> Any:
        """Validate and normalize an execution result (default: passthrough)."""
        return result


__all__ = ["Executor", "ExecutorContext", "ExecutionOptions"]
