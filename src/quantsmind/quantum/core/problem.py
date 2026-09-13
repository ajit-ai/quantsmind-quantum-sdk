"""The central domain problem model of QuantsMind Quantum.

A :class:`QuantumProblem` bundles identity, description, domain context,
variables, objectives, constraints, metadata, an optional formulation,
a preferred computation strategy and provenance.  It is the input object
that flows through formulation, strategy selection, mapping, execution and
solution reporting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

from quantsmind.quantum.core.constraint import Constraint
from quantsmind.quantum.core.domain_context import DomainContext
from quantsmind.quantum.core.objective import Objective
from quantsmind.quantum.core.variable import Variable


@dataclass
class QuantumProblem:
    """A domain problem that a QuantsMind Quantum workflow can process.

    Args:
        name: Unique problem name.
        description: Optional human-readable description.
        domain: Domain context, or a plain domain string coerced to one.
        variables: Decision variables of the problem.
        objectives: Objectives to optimise.
        constraints: Feasibility constraints.
        metadata: Free-form metadata (used by formulation detection, e.g.
            ``{"model_kind": "graph"}`` or ``{"encoding": {...}}``).
        formulation: Optional formulation model attached to the problem.
        preferred_strategy: Optional preferred computation strategy
            (a :class:`ComputationStrategy` or its name).
        provenance: Optional record of how the problem was assembled.

    Raises:
        ValueError: If the name is empty or names repeat within a category.
    """

    name: str
    description: str = ""
    domain: DomainContext | str | None = None
    variables: list[Variable] = field(default_factory=list)
    objectives: list[Objective] = field(default_factory=list)
    constraints: list[Constraint] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    formulation: Any = None  # MathematicalModel, set by the workflow
    preferred_strategy: Any = None  # ComputationStrategy | str | None
    provenance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("problem name must be a non-empty string")
        if isinstance(self.domain, str):
            self.domain = DomainContext(domain=self.domain)
        self._validate_unique_names()
        if isinstance(self.preferred_strategy, str):
            from quantsmind.quantum.strategy.strategy import ComputationStrategy

            self.preferred_strategy = ComputationStrategy.parse(self.preferred_strategy)

    def _validate_unique_names(self) -> None:
        self._assert_unique("variable", [v.name for v in self.variables])
        self._assert_unique("objective", [o.name for o in self.objectives])
        self._assert_unique("constraint", [c.name for c in self.constraints])

    @staticmethod
    def _assert_unique(kind: str, names: list[str]) -> None:
        seen: set[str] = set()
        duplicates: list[str] = []
        for name in names:
            if name in seen:
                duplicates.append(name)
            seen.add(name)
        if duplicates:
            raise ValueError(f"duplicate {kind} name(s): {sorted(set(duplicates))}")

    # -- mutation helpers ------------------------------------------------

    def add_variable(self, variable: Variable) -> Variable:
        """Add a variable (duplicate names are rejected)."""
        if variable.name in self.variable_names:
            raise ValueError(f"duplicate variable name {variable.name!r}")
        self.variables.append(variable)
        return variable

    def add_objective(self, objective: Objective) -> Objective:
        """Add an objective (duplicate names are rejected)."""
        if objective.name in self.objective_names:
            raise ValueError(f"duplicate objective name {objective.name!r}")
        self.objectives.append(objective)
        return objective

    def add_constraint(self, constraint: Constraint) -> Constraint:
        """Add a constraint (duplicate names are rejected)."""
        if constraint.name in self.constraint_names:
            raise ValueError(f"duplicate constraint name {constraint.name!r}")
        self.constraints.append(constraint)
        return constraint

    def variable(self, name: str) -> Variable:
        """Return the variable with the given name."""
        for variable in self.variables:
            if variable.name == name:
                return variable
        raise KeyError(f"variable {name!r} not in problem {self.name!r}")

    def objective(self, name: str) -> Objective:
        """Return the objective with the given name."""
        for objective in self.objectives:
            if objective.name == name:
                return objective
        raise KeyError(f"objective {name!r} not in problem {self.name!r}")

    def constraint(self, name: str) -> Constraint:
        """Return the constraint with the given name."""
        for constraint in self.constraints:
            if constraint.name == name:
                return constraint
        raise KeyError(f"constraint {name!r} not in problem {self.name!r}")

    # -- derived views ---------------------------------------------------

    @property
    def variable_names(self) -> list[str]:
        """Names of all variables."""
        return [v.name for v in self.variables]

    @property
    def objective_names(self) -> list[str]:
        """Names of all objectives."""
        return [o.name for o in self.objectives]

    @property
    def constraint_names(self) -> list[str]:
        """Names of all constraints."""
        return [c.name for c in self.constraints]

    @property
    def size(self) -> int:
        """Number of decision variables (the problem's effective size)."""
        return len(self.variables)

    # -- serialization ---------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        formulation = (
            self.formulation.to_dict()
            if self.formulation is not None and hasattr(self.formulation, "to_dict")
            else None
        )
        return {
            "name": self.name,
            "description": self.description,
            "domain": (
                cast(DomainContext, self.domain).to_dict() if self.domain is not None else None
            ),
            "variables": [v.to_dict() for v in self.variables],
            "objectives": [o.to_dict() for o in self.objectives],
            "constraints": [c.to_dict() for c in self.constraints],
            "metadata": dict(self.metadata),
            "formulation": formulation,
            "preferred_strategy": _strategy_label(self.preferred_strategy),
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QuantumProblem:
        """Rebuild a QuantumProblem from :meth:`to_dict` output."""
        problem = cls(
            name=str(data["name"]),
            description=str(data.get("description", "")),
            domain=(
                DomainContext.from_dict(data["domain"]) if data.get("domain") is not None else None
            ),
            variables=[Variable.from_dict(d) for d in data.get("variables", [])],
            objectives=[Objective.from_dict(d) for d in data.get("objectives", [])],
            constraints=[Constraint.from_dict(d) for d in data.get("constraints", [])],
            metadata=dict(data.get("metadata", {})),
            preferred_strategy=data.get("preferred_strategy"),
            provenance=dict(data.get("provenance", {})),
        )
        if data.get("formulation") is not None:
            from quantsmind.quantum.formulation import model_from_dict

            problem.formulation = model_from_dict(data["formulation"])
        return problem

    def __repr__(self) -> str:
        domain = cast(DomainContext, self.domain).qualified() if self.domain is not None else None
        return (
            f"QuantumProblem(name={self.name!r}, domain={domain}"
            f", variables={len(self.variables)}, objectives={len(self.objectives)}, "
            f"constraints={len(self.constraints)})"
        )


def _strategy_label(strategy: Any) -> str | None:
    """Return the serialized label of a strategy member or string."""
    if strategy is None:
        return None
    name = getattr(strategy, "name", strategy)
    return str(name).lower()


__all__ = ["QuantumProblem"]
