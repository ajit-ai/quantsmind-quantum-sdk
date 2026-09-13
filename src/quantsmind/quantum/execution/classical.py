"""Classical executor on top of the exact exhaustive baseline (QMQ-04 §6).

This wraps :class:`~quantsmind.quantum.optimization.classical.ExhaustiveSolver`
behind the common :class:`Executor` interface.  The solver is reused
unchanged — no second classical path is added.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from quantsmind.quantum.core.problem import QuantumProblem
from quantsmind.quantum.execution.errors import ClassicalExecutionError
from quantsmind.quantum.execution.evaluation import (
    feasibility_predicate,
    objective_evaluator,
)
from quantsmind.quantum.execution.executor import Executor, ExecutorContext
from quantsmind.quantum.execution.options import ExecutionOptions
from quantsmind.quantum.optimization.classical import (
    ClassicalSolverResult,
    ExhaustiveLimitError,
    ExhaustiveSolver,
    NoFeasibleSolutionError,
)
from quantsmind.quantum.strategy.strategy import ComputationStrategy


@dataclass
class ClassicalExecutionResult:
    """Normalized classical execution result.

    Leg identity is ``"classical"``; :attr:`executor`/:attr:`solver` keep the
    legacy label ``"classical/exhaustive"`` so provenance serialization does
    not change.
    """

    leg: str = "classical"
    solver: str = "classical/exhaustive"
    executor: str = "classical/exhaustive"
    algorithm: str = "exhaustive"
    assignment: dict[str, int] = field(default_factory=dict)
    energy: float = 0.0
    objective_value: float | None = None
    feasible: bool = True
    num_evaluations: int = 0
    num_feasible: int = 0
    limit: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "leg": self.leg,
            "solver": self.solver,
            "executor": self.executor,
            "algorithm": self.algorithm,
            "assignment": {k: int(v) for k, v in self.assignment.items()},
            "energy": self.energy,
            "objective_value": self.objective_value,
            "feasible": self.feasible,
            "num_evaluations": self.num_evaluations,
            "num_feasible": self.num_feasible,
            "limit": self.limit,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ClassicalExecutionResult:
        """Rebuild a result from :meth:`to_dict` output."""
        return cls(
            leg=str(data.get("leg", "classical")),
            solver=str(data.get("solver", "classical/exhaustive")),
            executor=str(data.get("executor", "classical/exhaustive")),
            algorithm=str(data.get("algorithm", "exhaustive")),
            assignment={str(k): int(v) for k, v in data.get("assignment", {}).items()},
            energy=float(data.get("energy", 0.0)),
            objective_value=(
                float(data["objective_value"]) if data.get("objective_value") is not None else None
            ),
            feasible=bool(data.get("feasible", True)),
            num_evaluations=int(data.get("num_evaluations", 0)),
            num_feasible=int(data.get("num_feasible", 0)),
            limit=int(data.get("limit", 0)),
            metadata=dict(data.get("metadata", {})),
        )

    @classmethod
    def from_solver(
        cls,
        result: ClassicalSolverResult,
        *,
        objective_value: float | None,
        feasible: bool,
        options: ExecutionOptions,
    ) -> ClassicalExecutionResult:
        """Normalize an :class:`ClassicalSolverResult` into an execution result."""
        return cls(
            assignment=dict(result.assignment),
            energy=float(result.energy),
            objective_value=objective_value,
            feasible=feasible,
            num_evaluations=int(result.num_evaluations),
            num_feasible=int(result.num_feasible),
            limit=int(result.limit),
            metadata={
                **dict(result.metadata),
                "optimization_level": options.optimization_level,
                "seed": options.seed,
            },
        )

    def __repr__(self) -> str:
        return (
            f"ClassicalExecutionResult(energy={self.energy}, "
            f"feasible={self.feasible}, evaluated={self.num_evaluations})"
        )


class ClassicalExecutor(Executor):
    """Exact-solution classical leg of an execution.

    Args:
        solver: Optional :class:`ExhaustiveSolver` override (workflows reuse
            their configured classical executor solver here).
    """

    name = "classical-executor"
    executor_id = "classical"
    strategies = (ComputationStrategy.CLASSICAL,)

    def __init__(self, *, solver: ExhaustiveSolver | None = None) -> None:
        self.solver = solver

    def prepare(self, context: ExecutorContext) -> None:
        if context.qubo is None:
            raise ClassicalExecutionError(
                "classical execution requires a QUBO mapping; the plan must map the problem first"
            )
        return None

    def execute(self, context: ExecutorContext) -> ClassicalExecutionResult:
        self.prepare(context)
        qubo = context.qubo
        if qubo is None:
            raise ClassicalExecutionError(
                "classical execution requires a QUBO mapping; the plan must map the problem first"
            )
        problem: QuantumProblem = context.problem
        solver = self.solver if self.solver is not None else ExhaustiveSolver()
        try:
            raw = solver.solve(
                qubo,
                is_feasible=feasibility_predicate(problem),
                objective_fn=objective_evaluator(problem),
            )
        except ExhaustiveLimitError as exc:
            raise ClassicalExecutionError(
                f"exhaustive classical execution rejected: {exc}"
            ) from exc
        except NoFeasibleSolutionError as exc:
            raise ClassicalExecutionError(
                f"classical execution found no feasible assignment: {exc}"
            ) from exc
        return ClassicalExecutionResult.from_solver(
            raw,
            objective_value=raw.objective_value,
            feasible=bool(raw.feasible),
            options=context.options,
        )

    def validate(
        self,
        result: ClassicalExecutionResult,
        context: ExecutorContext,
    ) -> ClassicalExecutionResult:
        if not isinstance(result, ClassicalExecutionResult):
            raise ClassicalExecutionError(
                f"classical executor produced {type(result).__name__}, "
                "expected ClassicalExecutionResult"
            )
        return result


__all__ = ["ClassicalExecutor", "ClassicalExecutionResult"]
