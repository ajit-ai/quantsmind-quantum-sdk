"""Objectives of quantum domain problems.

An objective describes what a workflow should optimise (``minimize cost``,
``maximize return``, ...).  It carries enough information to participate in
formulation and strategy selection: a sense, an optional expression, and a
weight used when objectives are combined.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

# An objective expression maps variable assignments to a scalar.  A symbolic
# string (e.g. ``"x1 + 2*x2"``) is accepted structurally but evaluation of
# symbolic strings arrives with the formulation capabilities of QMQ-02.
Expression = Callable[[dict[str, Any]], float] | str | None


class ObjectiveSense(Enum):
    """Optimisation sense of an objective.

    Attributes:
        MINIMIZE: Prefer lower objective values (e.g. cost, risk, latency).
        MAXIMIZE: Prefer higher objective values (e.g. return, throughput).
    """

    MINIMIZE = auto()
    MAXIMIZE = auto()

    @classmethod
    def parse(cls, value: Any) -> ObjectiveSense:
        """Coerce ``"min"``/``"max"`` (or a member) to :class:`ObjectiveSense`."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower()
        if text in {"min", "minimize"}:
            return cls.MINIMIZE
        if text in {"max", "maximize"}:
            return cls.MAXIMIZE
        raise ValueError(f"unknown objective sense {value!r}; expected 'minimize' or 'maximize'")


@dataclass
class Objective:
    """A scalar objective of a :class:`QuantumProblem`.

    Args:
        name: Unique objective name.
        sense: MINIMIZE or MAXIMIZE.
        expression: Callable(assignments) -> float, a symbolic string, or None.
        weight: Non-negative scaling weight used when objectives are combined.
        metadata: Free-form metadata.

    Raises:
        ValueError: If the name is empty or the weight is negative.
    """

    name: str
    sense: ObjectiveSense
    expression: Expression = None
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("objective name must be a non-empty string")
        self.sense = ObjectiveSense.parse(self.sense)
        if self.weight < 0:
            raise ValueError(f"objective {self.name!r} weight must be >= 0, got {self.weight}")

    @classmethod
    def minimize(
        cls, name: str, expression: Expression = None, *, weight: float = 1.0
    ) -> Objective:
        """Create a MINIMIZE objective."""
        return cls(name, ObjectiveSense.MINIMIZE, expression=expression, weight=weight)

    @classmethod
    def maximize(
        cls, name: str, expression: Expression = None, *, weight: float = 1.0
    ) -> Objective:
        """Create a MAXIMIZE objective."""
        return cls(name, ObjectiveSense.MAXIMIZE, expression=expression, weight=weight)

    def evaluate(self, assignments: dict[str, Any]) -> float | None:
        """Evaluate the objective against variable assignments.

        Callable expressions are evaluated directly.  Symbolic string (and
        :class:`~quantsmind.quantum.optimization.expression.Expression`)
        expressions are parsed and evaluated by the QMQ-02 expression model
        without ``eval()``.
        """
        if self.expression is None:
            return None
        if isinstance(self.expression, str):
            from quantsmind.quantum.optimization.expression import (
                parse_expression,
            )

            return float(parse_expression(self.expression).evaluate(assignments))
        if hasattr(self.expression, "evaluate"):
            return float(self.expression.evaluate(assignments))
        return float(self.expression(assignments))

    def describe(self) -> str:
        """Return a human-readable description, e.g. ``"minimize cost"``."""
        return f"{self.sense.name.lower()} {self.name}"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary.

        Callable expressions cannot be serialized and are stored as ``None``.
        """
        expression = self.expression if isinstance(self.expression, str) else None
        return {
            "name": self.name,
            "sense": self.sense.name.lower(),
            "expression": expression,
            "weight": self.weight,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Objective:
        """Rebuild an Objective from :meth:`to_dict` output."""
        return cls(
            name=str(data["name"]),
            sense=ObjectiveSense.parse(data.get("sense", "minimize")),
            expression=data.get("expression"),
            weight=float(data.get("weight", 1.0)),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return f"Objective(name={self.name!r}, sense={self.sense.name.lower()})"


__all__ = ["Expression", "Objective", "ObjectiveSense"]
