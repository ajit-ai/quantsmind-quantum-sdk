"""Optimization formulation of quantum domain problems.

An :class:`OptimizationModel` is a :class:`MathematicalModel` specialised
for optimization problems: it snapshots objective senses, variable bounds
and a constant term from the originating problem, and keeps a reference to
that problem so QMQ-02 evaluation methods (:meth:`objective_value`,
:meth:`constraint_values`, :meth:`is_feasible`) can operate on real
expressions.

The problem reference is **not** serialized: rebuilding a model from
:meth:`from_dict` yields a structural snapshot in which the evaluation
methods raise a :class:`ValueError` explaining that the model must be built
from a problem first.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from quantsmind.quantum.core.constraint import ConstraintStatus
from quantsmind.quantum.formulation.mathematical_model import MathematicalModel

if TYPE_CHECKING:
    from quantsmind.quantum.core.problem import QuantumProblem

if TYPE_CHECKING:
    from quantsmind.quantum.core.problem import QuantumProblem


@dataclass
class OptimizationModel(MathematicalModel):
    """Structural formulation of an optimization problem.

    Args:
        objective_senses: Objective name -> ``"minimize"``/``"maximize"``.
        variable_bounds: Variable name -> ``[lower_bound, upper_bound]``.
        constant_term: Additive constant of the (single) objective.
        problem_ref: Reference to the originating problem (not serialized).
    """

    objective_senses: dict[str, str] = field(default_factory=dict)
    variable_bounds: dict[str, list[Any]] = field(default_factory=dict)
    constant_term: float = 0.0
    problem_ref: QuantumProblem | None = field(default=None, repr=False, compare=False)

    kind: ClassVar[str] = "optimization"

    @classmethod
    def from_problem(cls, problem: QuantumProblem) -> OptimizationModel:
        """Snapshot an optimization problem including senses and bounds."""
        model = super().from_problem(problem)
        model.objective_senses = {o.name: o.sense.name.lower() for o in problem.objectives}
        model.variable_bounds = {v.name: [v.lower_bound, v.upper_bound] for v in problem.variables}
        model.constant_term = 0.0
        model.problem_ref = problem
        return model

    # -- evaluation -------------------------------------------------------

    def _source_problem(self) -> QuantumProblem:
        if self.problem_ref is None:
            raise ValueError(
                "this OptimizationModel has no source problem; rebuild it "
                "with OptimizationModel.from_problem(problem)"
            )
        return self.problem_ref

    def objective_value(self, assignment: dict[str, Any]) -> float | None:
        """Evaluate the first objective against an assignment (or ``None``).

        Raises:
            ValueError: If the model has no source problem reference.
        """
        problem = self._source_problem()
        if not problem.objectives:
            return None
        return problem.objectives[0].evaluate(assignment)

    def constraint_values(self, assignment: dict[str, Any]) -> dict[str, float | None]:
        """Evaluate every constraint expression against an assignment.

        Returns a mapping of constraint name -> numeric left-hand side
        (``None`` when the constraint has no expression).
        """
        from quantsmind.quantum.optimization.expression import (
            evaluate_expression,
        )

        problem = self._source_problem()
        values: dict[str, float | None] = {}
        for constraint in problem.constraints:
            if constraint.expression is None:
                values[constraint.name] = None
            else:
                values[constraint.name] = float(
                    evaluate_expression(constraint.expression, assignment)
                )
        return values

    def is_feasible(self, assignment: dict[str, Any]) -> bool:
        """Return whether the assignment satisfies every constraint."""
        problem = self._source_problem()
        return all(
            constraint.evaluate(assignment) is not ConstraintStatus.VIOLATED
            for constraint in problem.constraints
        )

    # -- serialization ----------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary (problem reference excluded)."""
        data = super().to_dict()
        data["objective_senses"] = dict(self.objective_senses)
        data["variable_bounds"] = {
            name: list(bounds) for name, bounds in self.variable_bounds.items()
        }
        data["constant_term"] = self.constant_term
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OptimizationModel:
        """Rebuild an OptimizationModel from :meth:`to_dict` output."""
        model = cls(
            name=str(data.get("name", "model")),
            problem_name=str(data.get("problem_name", "")),
            variables=[str(v) for v in data.get("variables", [])],
            objectives=[str(o) for o in data.get("objectives", [])],
            constraints=[str(c) for c in data.get("constraints", [])],
            metadata=dict(data.get("metadata", {})),
        )
        model.objective_senses = dict(data.get("objective_senses", {}))
        model.variable_bounds = {
            str(name): list(bounds) for name, bounds in data.get("variable_bounds", {}).items()
        }
        model.constant_term = float(data.get("constant_term", 0.0))
        return model


__all__ = ["OptimizationModel"]
