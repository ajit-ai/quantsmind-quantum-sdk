"""Constraints of quantum domain problems.

A constraint restricts the feasible assignments of a
:class:`QuantumProblem`.  QMQ-01 keeps the representation extensible
(``<=``, ``>=``, ``==``, hard/soft classification, optional penalty) but
does not build a symbolic mathematics engine; that arrives with the
formulation capabilities of QMQ-02.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

# Tolerance used when checking equality constraints against a numeric value.
_EQ_TOLERANCE = 1e-9


class ConstraintOperator(Enum):
    """Relational operator of a constraint.

    Attributes:
        LE: ``expression <= value``
        GE: ``expression >= value``
        EQ: ``expression == value``
    """

    LE = "<="
    GE = ">="
    EQ = "=="

    @classmethod
    def parse(cls, value: Any) -> ConstraintOperator:
        """Coerce a symbol (``"<="``, ``">="``, ``"=="``) to an operator."""
        if isinstance(value, cls):
            return value
        text = str(value).strip()
        for member in cls:
            if member.value == text or member.name.lower() == text.lower():
                return member
        raise ValueError(f"unknown constraint operator {value!r}; expected one of: <=, >=, ==")


class ConstraintPriority(Enum):
    """Hard/soft classification of a constraint.

    Attributes:
        HARD: Must be satisfied for a solution to be feasible.
        SOFT: Desirable; violations may be traded via ``penalty``.
    """

    HARD = auto()
    SOFT = auto()

    @classmethod
    def parse(cls, value: Any) -> ConstraintPriority:
        """Coerce ``"hard"``/``"soft"`` (or a member) to a priority."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower()
        for member in cls:
            if member.name.lower() == text:
                return member
        raise ValueError(f"unknown constraint priority {value!r}; expected 'hard' or 'soft'")


class ConstraintStatus(Enum):
    """Evaluation status of a constraint against an assignment.

    Attributes:
        SATISFIED: The constraint holds for the evaluated assignments.
        VIOLATED: The constraint does not hold.
        UNKNOWN: The constraint could not be evaluated (no expression).
    """

    SATISFIED = auto()
    VIOLATED = auto()
    UNKNOWN = auto()


@dataclass
class Constraint:
    """A constraint of a :class:`QuantumProblem`.

    Args:
        name: Unique constraint name.
        expression: Callable(assignments) -> float, a symbolic string, or None.
        operator: Comparison operator (``<=``, ``>=``, ``==``).
        value: RHS constant the expression is compared against.
        priority: HARD or SOFT classification.
        penalty: Optional penalty weight applied when a SOFT constraint is
            violated (used by later formulation phases).
        metadata: Free-form metadata.

    Raises:
        ValueError: If the name is empty or the penalty is negative.
    """

    name: str
    expression: Callable[[dict[str, Any]], float] | str | None = None
    operator: ConstraintOperator = ConstraintOperator.LE
    value: float = 0.0
    priority: ConstraintPriority = ConstraintPriority.HARD
    penalty: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("constraint name must be a non-empty string")
        self.operator = ConstraintOperator.parse(self.operator)
        self.priority = ConstraintPriority.parse(self.priority)
        if self.penalty < 0:
            raise ValueError(f"constraint {self.name!r} penalty must be >= 0, got {self.penalty}")

    @classmethod
    def le(
        cls,
        name: str,
        expression: Callable[[dict[str, Any]], float] | str | None = None,
        value: float = 0.0,
        *,
        priority: ConstraintPriority | str = ConstraintPriority.HARD,
        penalty: float = 0.0,
    ) -> Constraint:
        """Create a ``<=`` constraint."""
        return cls(
            name,
            expression,
            ConstraintOperator.LE,
            value,
            ConstraintPriority.parse(priority),
            penalty,
        )

    @classmethod
    def ge(
        cls,
        name: str,
        expression: Callable[[dict[str, Any]], float] | str | None = None,
        value: float = 0.0,
        *,
        priority: ConstraintPriority | str = ConstraintPriority.HARD,
        penalty: float = 0.0,
    ) -> Constraint:
        """Create a ``>=`` constraint."""
        return cls(
            name,
            expression,
            ConstraintOperator.GE,
            value,
            ConstraintPriority.parse(priority),
            penalty,
        )

    @classmethod
    def eq(
        cls,
        name: str,
        expression: Callable[[dict[str, Any]], float] | str | None = None,
        value: float = 0.0,
        *,
        priority: ConstraintPriority | str = ConstraintPriority.HARD,
        penalty: float = 0.0,
    ) -> Constraint:
        """Create an ``==`` constraint."""
        return cls(
            name,
            expression,
            ConstraintOperator.EQ,
            value,
            ConstraintPriority.parse(priority),
            penalty,
        )

    def compare(self, lhs: float) -> ConstraintStatus:
        """Compare an evaluated expression against the constraint value."""
        if self.operator is ConstraintOperator.LE:
            return ConstraintStatus.SATISFIED if lhs <= self.value else ConstraintStatus.VIOLATED
        if self.operator is ConstraintOperator.GE:
            return ConstraintStatus.SATISFIED if lhs >= self.value else ConstraintStatus.VIOLATED
        ok = abs(lhs - self.value) <= _EQ_TOLERANCE
        return ConstraintStatus.SATISFIED if ok else ConstraintStatus.VIOLATED

    def evaluate(self, assignments: dict[str, Any]) -> ConstraintStatus:
        """Evaluate the constraint against variable assignments.

        Constraints without an expression report :data:`ConstraintStatus.UNKNOWN`.
        Symbolic string (and expression-node) expressions are parsed and
        evaluated by the QMQ-02 expression model without ``eval()``.
        """
        if self.expression is None:
            return ConstraintStatus.UNKNOWN
        if isinstance(self.expression, str):
            from quantsmind.quantum.optimization.expression import (
                parse_expression,
            )

            lhs = float(parse_expression(self.expression).evaluate(assignments))
            return self.compare(lhs)
        if hasattr(self.expression, "evaluate"):
            return self.compare(float(self.expression.evaluate(assignments)))
        return self.compare(float(self.expression(assignments)))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary.

        Callable expressions cannot be serialized and are stored as ``None``.
        """
        expression = self.expression if isinstance(self.expression, str) else None
        return {
            "name": self.name,
            "expression": expression,
            "operator": self.operator.value,
            "value": self.value,
            "priority": self.priority.name.lower(),
            "penalty": self.penalty,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Constraint:
        """Rebuild a Constraint from :meth:`to_dict` output."""
        return cls(
            name=str(data["name"]),
            expression=data.get("expression"),
            operator=ConstraintOperator.parse(data.get("operator", "<=")),
            value=float(data.get("value", 0.0)),
            priority=ConstraintPriority.parse(data.get("priority", "hard")),
            penalty=float(data.get("penalty", 0.0)),
            metadata=dict(data.get("metadata", {})),
        )

    def __repr__(self) -> str:
        return (
            f"Constraint(name={self.name!r}, op={self.operator.value}, "
            f"value={self.value}, priority={self.priority.name.lower()})"
        )


__all__ = [
    "Constraint",
    "ConstraintOperator",
    "ConstraintPriority",
    "ConstraintStatus",
]
