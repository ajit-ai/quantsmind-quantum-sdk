"""Solutions produced for quantum domain problems.

A :class:`ProblemSolution` is a **domain** solution: it carries variable
assignments, objective values, constraint status, a score and feasibility.
It is deliberately disconnected from any raw MicroQuantum circuit result —
those remain accessible through the execution layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.core.constraint import ConstraintStatus
from quantsmind.quantum.core.objective import ObjectiveSense

if TYPE_CHECKING:
    from quantsmind.quantum.core.problem import QuantumProblem


@dataclass
class ProblemSolution:
    """A domain-level solution to a :class:`QuantumProblem`.

    Args:
        problem_name: Name of the problem this solution satisfies.
        assignments: Variable name -> assigned value.
        objective_values: Objective name -> evaluated value.
        constraint_status: Constraint name -> evaluation status.
        score: Optional combined, sense-aware score (higher is better).
        feasible: Whether all constraints are satisfied (none violated).
        metadata: Free-form solution metadata (backend, shots, ...).
    """

    problem_name: str = ""
    assignments: dict[str, Any] = field(default_factory=dict)
    objective_values: dict[str, float] = field(default_factory=dict)
    constraint_status: dict[str, ConstraintStatus] = field(default_factory=dict)
    score: float | None = None
    feasible: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_names(
        cls,
        problem_name: str,
        variable_names: list[str],
        objective_names: list[str],
        constraint_names: list[str],
    ) -> ProblemSolution:
        """Build an empty solution skeleton matching a problem's structure."""
        return cls(
            problem_name=problem_name,
            assignments={name: None for name in variable_names},
            objective_values={name: 0.0 for name in objective_names},
            constraint_status={name: ConstraintStatus.UNKNOWN for name in constraint_names},
        )

    def evaluate(self, problem: QuantumProblem) -> ProblemSolution:
        """Populate objective values and constraint status from assignments.

        Only callable expressions participate (symbolic strings raise by
        design until QMQ-02 formulation support lands).  Feasibility is
        recomputed from the resulting statuses.
        """
        for objective in problem.objectives:
            value = objective.evaluate(self.assignments)
            if value is not None:
                self.objective_values[objective.name] = value
        for constraint in problem.constraints:
            self.constraint_status[constraint.name] = constraint.evaluate(self.assignments)
        self.feasible = self.is_feasible()
        return self

    def is_feasible(self) -> bool:
        """Return True when no constraint is violated (unknowns are benign)."""
        return all(
            status is not ConstraintStatus.VIOLATED for status in self.constraint_status.values()
        )

    def compute_score(self, problem: QuantumProblem) -> float | None:
        """Weighted, sense-aware objective score (higher is better).

        Maximizing objectives contribute ``weight * value``; minimizing
        objectives contribute ``-weight * value``.  Returns ``None`` when no
        objective could be evaluated.
        """
        total = 0.0
        evaluated = 0
        for objective in problem.objectives:
            value = objective.evaluate(self.assignments)
            if value is None:
                continue
            contribution = objective.weight * value
            if objective.sense is ObjectiveSense.MINIMIZE:
                contribution = -contribution
            total += contribution
            evaluated += 1
        return total if evaluated else None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "problem_name": self.problem_name,
            "assignments": dict(self.assignments),
            "objective_values": dict(self.objective_values),
            "constraint_status": {
                name: status.name.lower() for name, status in self.constraint_status.items()
            },
            "score": self.score,
            "feasible": self.feasible,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProblemSolution:
        """Rebuild a ProblemSolution from :meth:`to_dict` output."""
        return cls(
            problem_name=str(data.get("problem_name", "")),
            assignments=dict(data.get("assignments", {})),
            objective_values={
                name: float(value) for name, value in data.get("objective_values", {}).items()
            },
            constraint_status={
                name: ConstraintStatus[status.upper()]
                for name, status in data.get("constraint_status", {}).items()
            },
            score=(float(data["score"]) if data.get("score") is not None else None),
            feasible=bool(data.get("feasible", False)),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"ProblemSolution(problem={self.problem_name!r}, "
            f"variables={len(self.assignments)}, feasible={self.feasible}, "
            f"score={self.score})"
        )


__all__ = ["ProblemSolution"]
