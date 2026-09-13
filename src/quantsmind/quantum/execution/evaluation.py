"""Evaluation helpers shared by every QMQ-04 executor.

These are the single source of truth for turning a candidate assignment
into feasibility/objective facts, so the classical and quantum legs (and
their validation) cannot disagree about a problem's semantics.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from quantsmind.quantum.core.constraint import ConstraintStatus

if TYPE_CHECKING:
    from quantsmind.quantum.core.problem import QuantumProblem


def feasibility_predicate(problem: QuantumProblem) -> Callable[[dict[str, int]], bool]:
    """Return a predicate marking an assignment feasible iff no constraint
    is violated (unknowns are benign)."""

    def is_feasible(assignment: dict[str, int]) -> bool:
        return all(
            constraint.evaluate(assignment) is not ConstraintStatus.VIOLATED
            for constraint in problem.constraints
        )

    return is_feasible


def is_feasible_assignment(problem: QuantumProblem, assignment: dict[str, int]) -> bool:
    """Evaluate domain feasibility of a candidate assignment."""
    return feasibility_predicate(problem)(assignment)


def objective_evaluator(problem: QuantumProblem) -> Callable[[dict[str, int]], float]:
    """Return an evaluator for the first objective (0.0 when absent).

    This mirrors the workflow baseline: only the first objective participates
    in scalar comparisons; all objectives are reported separately.
    """
    from quantsmind.quantum.core.objective import Objective

    objective: Objective | None = problem.objectives[0] if problem.objectives else None

    def evaluate(assignment: dict[str, int]) -> float:
        if objective is None:
            return 0.0
        value = objective.evaluate(assignment)
        return 0.0 if value is None else float(value)

    return evaluate


def objective_values(problem: QuantumProblem, assignment: dict[str, int]) -> dict[str, float]:
    """Evaluate every objective for an assignment (only evaluable ones)."""
    values: dict[str, float] = {}
    for objective in problem.objectives:
        value = objective.evaluate(assignment)
        if value is not None:
            values[objective.name] = float(value)
    return values


def objective_value(problem: QuantumProblem, assignment: dict[str, int]) -> float | None:
    """Scalar objective value of the first objective (or ``None``)."""
    values = objective_values(problem, assignment)
    first = problem.objectives[0].name if problem.objectives else None
    return values.get(first) if first is not None else None


__all__ = [
    "feasibility_predicate",
    "is_feasible_assignment",
    "objective_evaluator",
    "objective_values",
    "objective_value",
]
