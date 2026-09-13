"""Mathematical formulation foundation for quantum domain problems.

A :class:`MathematicalModel` sits between a
:class:`~quantsmind.quantum.core.problem.QuantumProblem` and computational
execution.  It records which variables, objectives and constraints
participate, and which family the problem belongs to (optimization, graph,
ML, simulation or statistical).  Concrete computational representations
(QUBO, Ising, Hamiltonians, circuits) are layered on top in QMQ-02.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, Self

if TYPE_CHECKING:
    from quantsmind.quantum.core.problem import QuantumProblem


@dataclass
class MathematicalModel:
    """A structural formulation of a domain problem.

    Args:
        name: Formulation name.
        problem_name: Name of the originating problem.
        variables: Names of the participating variables.
        objectives: Names of the participating objectives.
        constraints: Names of the participating constraints.
        metadata: Formulation metadata (copied from the problem).

    Attributes:
        kind: Machine-readable formulation family, overridden by subclasses.
    """

    name: str = "model"
    problem_name: str = ""
    variables: list[str] = field(default_factory=list)
    objectives: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    kind: ClassVar[str] = "mathematical"

    @classmethod
    def from_problem(cls, problem: QuantumProblem) -> Self:
        """Snapshot a domain problem into a mathematical model.

        Constructs a concrete instance of ``cls`` so subclasses reading
        extra state after a ``super().from_problem`` call are always
        operating on their own type.
        """
        return cls(
            name=f"{problem.name}_model",
            problem_name=problem.name,
            variables=[v.name for v in problem.variables],
            objectives=[o.name for o in problem.objectives],
            constraints=[c.name for c in problem.constraints],
            metadata=dict(problem.metadata),
        )

    @property
    def n_variables(self) -> int:
        """Number of participating variables."""
        return len(self.variables)

    @property
    def n_objectives(self) -> int:
        """Number of participating objectives."""
        return len(self.objectives)

    @property
    def n_constraints(self) -> int:
        """Number of participating constraints."""
        return len(self.constraints)

    def describe(self) -> str:
        """Return a one-line description of the formulation."""
        return (
            f"{self.kind} formulation for problem {self.problem_name!r}: "
            f"{self.n_variables} variables, {self.n_objectives} objectives, "
            f"{self.n_constraints} constraints"
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "kind": self.kind,
            "name": self.name,
            "problem_name": self.problem_name,
            "variables": list(self.variables),
            "objectives": list(self.objectives),
            "constraints": list(self.constraints),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MathematicalModel:
        """Rebuild a MathematicalModel from :meth:`to_dict` output.

        Subclasses reuse this constructor because their extra fields have
        defaults; any subclass-specific keys are re-collected by their own
        overridden ``from_dict``.
        """
        return cls(
            name=str(data.get("name", "model")),
            problem_name=str(data.get("problem_name", "")),
            variables=[str(v) for v in data.get("variables", [])],
            objectives=[str(o) for o in data.get("objectives", [])],
            constraints=[str(c) for c in data.get("constraints", [])],
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return f"<{self.kind} formulation of problem {self.problem_name!r}>"


__all__ = ["MathematicalModel"]
