"""Constraint -> QUBO penalty transformation (QMQ-02).

Supported constraint classes (over binary variables ``x_i in {0,1}``):

* **equality** ``sum(c_i * x_i) + c0 == value`` -> ``P * (lhs - value)^2``
* **inequality** ``sum(c_i * x_i) + c0 <= value`` -> equality with slack bits
  ``P * (sum(c_i*x_i) + sum(2^j * s_j) - (value - c0))^2`` where the slack
  bits cover every achievable deficit.  This requires integer coefficients
  (the deficits are integers); non-integer inequalities are rejected
  explicitly because a penalty would be mathematically incorrect.
* **greater-or-equal** is reduced to a ``<=`` constraint by negating all
  coefficients and the right-hand side (the reduced form may again require
  integer coefficients).

Unsupported constraint types (callable expressions, unknown operators,
quantities of degree > 1, or unsatisfiable inequalities) fail with
:class:`UnsupportedConstraintError` — never with a silent, wrong mapping.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from quantsmind.quantum.optimization.expression import (
    Expression,
    coerce_expression,
)

_EQ = "=="
_LE = "<="
_GE = ">="


class UnsupportedConstraintError(ValueError):
    """Raised when a constraint cannot be turned into a QUBO penalty."""


def _name_of(constraint: Any) -> str:
    name = getattr(constraint, "name", None)
    if not name:
        raise UnsupportedConstraintError("constraint must declare a name")
    return str(name)


def _operator_of(constraint: Any) -> str:
    operator = getattr(constraint, "operator", _LE)
    if hasattr(operator, "value"):
        return str(operator.value)
    return str(operator).strip().lower().replace(" ", "")


def _is_integer(value: float, tolerance: float = 1e-9) -> bool:
    return abs(value - round(value)) <= tolerance


@dataclass
class PenaltyTerm:
    """One expanded QUBO penalty term for a constraint.

    Args:
        constraint: Name of the originating constraint.
        operator: Serialized operator (``"=="``, ``"<="``, ``">="``).
        weight: Penalty multiplier ``P``.
        linear: Variable name -> linear coefficient.
        quadratic: ``(i, j)`` with ``i < j`` -> pairwise coefficient.
        constant: Additive penalty constant.
        slack_variables: Slack variables introduced for inequalities.
        expression: Human-readable residual squared, e.g.
            ``"P = 10.0 * (2*x0 + 3*x1 - 5)^2"``.
    """

    constraint: str
    operator: str
    weight: float
    linear: dict[str, float] = field(default_factory=dict)
    quadratic: dict[tuple[str, str], float] = field(default_factory=dict)
    constant: float = 0.0
    slack_variables: list[str] = field(default_factory=list)
    expression: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "constraint": self.constraint,
            "operator": self.operator,
            "weight": self.weight,
            "linear": {n: c for n, c in sorted(self.linear.items())},
            "quadratic": {
                f"{left},{right}": c for (left, right), c in sorted(self.quadratic.items())
            },
            "constant": self.constant,
            "slack_variables": list(self.slack_variables),
            "expression": self.expression,
        }


class ConstraintPenalizer:
    """Converts supported constraints into exact QUBO penalty terms.

    Args:
        penalty: Positive penalty multiplier ``P``.  When ``None`` a default
            of ``10.0`` is used.  The caller (typically the QUBO mapper)
            should scale ``P`` above the objective range so that violating a
            constraint can never be attractive.
    """

    def __init__(self, *, penalty: float | None = None) -> None:
        value = 10.0 if penalty is None else float(penalty)
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError(f"penalty must be a positive finite number, got {value!r}")
        self.penalty = value

    def penalize(self, constraint: Any) -> PenaltyTerm:
        """Return the QUBO penalty term expansion for a constraint.

        Raises:
            UnsupportedConstraintError: For unsupported constraint types.
        """
        name = _name_of(constraint)
        operator = _operator_of(constraint)
        expression = getattr(constraint, "expression", None)
        if expression is None:
            raise UnsupportedConstraintError(
                f"constraint {name!r} has no expression; cannot build a QUBO penalty"
            )
        if callable(expression) and not isinstance(expression, Expression):
            raise UnsupportedConstraintError(
                f"constraint {name!r} uses a callable expression; automatic "
                "penalty formulation requires a symbolic string expression"
            )
        value = float(getattr(constraint, "value", 0.0))
        residual = self._residual(name, operator, expression, value)
        coefficients, target = residual
        return self._square(name, operator, coefficients, target)

    def _residual(
        self,
        name: str,
        operator: str,
        expression: Any,
        value: float,
    ) -> tuple[dict[str, float], float]:
        """Return the linear coefficients and target of ``lhs OP value``.

        The residual is ``sum(c_i * x_i) - target`` (equality) or the
        slack-augmented equivalent (inequality).  The returned operator is
        the effective ``<=``/``==`` form after reduction.
        """
        symbol = coerce_expression(expression)
        monomials = symbol.expand()
        constant = 0.0
        coefficients: dict[str, float] = {}
        for monomial, coefficient in monomials.items():
            if len(monomial) == 0:
                constant += coefficient
            elif len(monomial) == 1:
                coefficients[monomial[0]] = coefficients.get(monomial[0], 0.0) + coefficient
            else:
                raise UnsupportedConstraintError(
                    f"constraint {name!r} has a term of degree {len(monomial)}; "
                    "only linear constraints can be penalised"
                )
        target = value - constant
        if operator == _EQ:
            return coefficients, target
        if operator == _GE:
            negated = {k: -v for k, v in coefficients.items()}
            return self._add_slack(name, negated, -target)
        if operator == _LE:
            return self._add_slack(name, coefficients, target)
        raise UnsupportedConstraintError(
            f"constraint {name!r} has unsupported operator {operator!r}"
        )

    def _add_slack(
        self,
        name: str,
        coefficients: dict[str, float],
        target: float,
    ) -> tuple[dict[str, float], float]:
        """Augment an inequality with slack bits so it becomes an equality."""
        for variable in coefficients:
            if not math.isfinite(coefficients[variable]):
                raise UnsupportedConstraintError(
                    f"constraint {name!r} has non-finite coefficient {coefficients[variable]!r}"
                )
        if not _is_integer(target):
            raise UnsupportedConstraintError(
                f"inequality {name!r} has a non-integer right-hand side "
                f"({target}); penalty formulation requires integer "
                "coefficients so the slack bits stay exact"
            )
        for variable, coefficient in coefficients.items():
            if not _is_integer(coefficient):
                raise UnsupportedConstraintError(
                    f"inequality {name!r} has a non-integer coefficient "
                    f"{coefficient!r} on {variable!r}; penalty formulation "
                    "requires integer coefficients"
                )
        min_lhs = sum(c for c in coefficients.values() if c < 0.0)
        max_deficit = target - min_lhs
        if max_deficit < 0.0:
            raise UnsupportedConstraintError(
                f"inequality {name!r} cannot be satisfied by any binary "
                "assignment (minimum left-hand side still exceeds the bound)"
            )
        slack_variables: list[str] = []
        deficit = int(round(max_deficit))
        for index in range(deficit.bit_length()):
            slack_variables.append(f"{name}_slack_{index}")
            coefficients[slack_variables[-1]] = float(2**index)
        return coefficients, target

    def _square(
        self,
        name: str,
        operator: str,
        coefficients: dict[str, float],
        target: float,
    ) -> PenaltyTerm:
        """Expand ``P * (sum(c_i x_i) - target)^2`` with x^2 = x."""
        weight = self.penalty
        linear: dict[str, float] = {}
        quadratic: dict[tuple[str, str], float] = {}
        for variable, coefficient in coefficients.items():
            linear[variable] = linear.get(variable, 0.0) + weight * (
                coefficient**2 - 2.0 * target * coefficient
            )
        ordered = list(coefficients)
        for index, left in enumerate(ordered):
            for right in ordered[index + 1 :]:
                key = (left, right) if left < right else (right, left)
                product = coefficients[left] * coefficients[right]
                if product != 0.0:
                    quadratic[key] = quadratic.get(key, 0.0) + 2.0 * weight * product
        constant = weight * target**2
        lhs = " + ".join(f"{coefficients[v]!r}*{v}" for v in ordered if coefficients[v] != 0.0)
        residual = f"({lhs} - {target!r})^2" if lhs else f"({-target!r})^2"
        expression = f"P = {weight!r} * {residual}"
        return PenaltyTerm(
            constraint=name,
            operator=operator,
            weight=weight,
            linear=linear,
            quadratic=quadratic,
            constant=constant,
            slack_variables=[v for v in coefficients if v.startswith(f"{name}_slack_")],
            expression=expression,
        )


__all__ = ["ConstraintPenalizer", "PenaltyTerm", "UnsupportedConstraintError"]
