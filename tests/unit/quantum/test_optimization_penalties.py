"""Tests for QMQ-02 constraint -> QUBO penalty formulation.

The key assertion is an exact identity: for every binary assignment (decision
variables **and** slack variables), the expanded :class:`PenaltyTerm` equals
``P * (sum(c_i * x_i) - target)**2`` — the penalty the mapper claims to have
built.  This validates the full expansion (linear, pairwise and constant
parts, including the ``-2*P*target*c_i`` cross terms).
"""

from __future__ import annotations

import itertools

import pytest

from quantsmind.quantum import Constraint
from quantsmind.quantum.optimization.expression import parse_expression
from quantsmind.quantum.optimization.penalties import (
    ConstraintPenalizer,
    PenaltyTerm,
    UnsupportedConstraintError,
)


def _term_energy(term: PenaltyTerm, assignment: dict[str, int]) -> float:
    value = term.constant
    for name, coefficient in term.linear.items():
        value += coefficient * assignment[name]
    for (left, right), coefficient in term.quadratic.items():
        value += coefficient * assignment[left] * assignment[right]
    return value


def _reduced(expression: str, value: float, operator: str) -> tuple[dict[str, float], float]:
    monomials = parse_expression(expression).expand()
    constant = sum(c for monomial, c in monomials.items() if not monomial)
    coefficients: dict[str, float] = {}
    for monomial, coefficient in monomials.items():
        if len(monomial) == 1:
            coefficients[monomial[0]] = coefficients.get(monomial[0], 0.0) + coefficient
    target = value - constant
    if operator == ">=":
        coefficients = {k: -v for k, v in coefficients.items()}
        target = -target
    return coefficients, target


def _slack_weights(term: PenaltyTerm) -> dict[str, float]:
    weights: dict[str, float] = {}
    for name in term.slack_variables:
        index = int(name.rsplit("_slack_", 1)[1])
        weights[name] = float(2**index)
    return weights


def _assert_penalty_identity(
    term: PenaltyTerm,
    coefficients: dict[str, float],
    target: float,
    weight: float,
) -> None:
    all_variables = sorted(
        set(coefficients) | set(term.linear) | {v for pair in term.quadratic for v in pair}
    )
    for bits in itertools.product([0, 1], repeat=len(all_variables)):
        assignment = dict(zip(all_variables, bits, strict=False))
        residual = sum(coefficients.get(v, 0.0) * assignment[v] for v in all_variables)
        residual -= target
        expected = weight * residual**2
        actual = _term_energy(term, assignment)
        assert abs(actual - expected) < 1e-9, (
            f"{assignment}: expected {expected}, term gives {actual}"
        )


class TestEquality:
    def test_exact_square(self) -> None:
        term = ConstraintPenalizer(penalty=2.0).penalize(
            Constraint.eq("sum", expression="x0 + x1", value=1.0)
        )
        coefficients, target = _reduced("x0 + x1", 1.0, "==")
        _assert_penalty_identity(term, coefficients, target, 2.0)
        assert term.slack_variables == []

    def test_value_zero(self) -> None:
        term = ConstraintPenalizer().penalize(Constraint.eq("c", expression="x0", value=0.0))
        # P * (x0 - 0)^2 = P * x0 for a binary variable.
        assert term.linear == {"x0": 10.0}
        assert term.constant == 0.0


class TestInequality:
    def test_le_with_slack_exact(self) -> None:
        term = ConstraintPenalizer(penalty=10.0).penalize(
            Constraint.le("cap", expression="2*x0 + 3*x1", value=5.0)
        )
        assert term.slack_variables == ["cap_slack_0", "cap_slack_1", "cap_slack_2"]
        weights = _slack_weights(term)
        coefficients, target = _reduced("2*x0 + 3*x1", 5.0, "<=")
        coefficients = {**coefficients, **weights}
        _assert_penalty_identity(term, coefficients, target, 10.0)

    def test_ge_reduced_to_le(self) -> None:
        term = ConstraintPenalizer(penalty=3.0).penalize(
            Constraint.ge("min", expression="x0 + x1", value=1.0)
        )
        # -(x0 + x1) <= -1 -> slack bits cover 0..1 deficits.
        assert term.slack_variables == ["min_slack_0"]
        coefficients, target = _reduced("x0 + x1", 1.0, ">=")
        coefficients = {**coefficients, **{"min_slack_0": 1.0}}
        _assert_penalty_identity(term, coefficients, target, 3.0)

    def test_feasible_assignments_reach_zero_penalty(self) -> None:
        term = ConstraintPenalizer(penalty=10.0).penalize(
            Constraint.le("cap", expression="x0 + x1", value=1.0)
        )
        assert term.slack_variables == ["cap_slack_0"]
        for bits in itertools.product([0, 1], repeat=2):
            decision = dict(zip(["x0", "x1"], bits, strict=False))
            lhs = bits[0] + bits[1]
            best = min(_term_energy(term, {**decision, "cap_slack_0": s}) for s in (0, 1))
            assert best == pytest.approx(0.0 if lhs <= 1 else 10.0 * (lhs - 1) ** 2)

    def test_no_slack_needed_when_tight(self) -> None:
        term = ConstraintPenalizer().penalize(Constraint.ge("c", expression="x0 + x1", value=2.0))
        # negated form -(x0 + x1) <= -2 has a zero maximum deficit.
        assert term.slack_variables == []


class TestUnsupported:
    def test_callable_expression_rejected(self) -> None:
        with pytest.raises(UnsupportedConstraintError, match="callable"):
            ConstraintPenalizer().penalize(
                Constraint.le("c", expression=lambda v: v["x"], value=1.0)
            )

    def test_missing_expression_rejected(self) -> None:
        with pytest.raises(UnsupportedConstraintError, match="no expression"):
            ConstraintPenalizer().penalize(Constraint.le("c", value=1.0))

    def test_degree_two_constraint_rejected(self) -> None:
        with pytest.raises(UnsupportedConstraintError, match="degree"):
            ConstraintPenalizer().penalize(Constraint.le("c", expression="x0*x1", value=1.0))

    def test_non_integer_coefficient_rejected(self) -> None:
        with pytest.raises(UnsupportedConstraintError, match="non-integer"):
            ConstraintPenalizer().penalize(Constraint.le("c", expression="x0 + 0.5*x1", value=3.0))

    def test_non_integer_rhs_rejected(self) -> None:
        with pytest.raises(UnsupportedConstraintError, match="non-integer"):
            ConstraintPenalizer().penalize(Constraint.le("c", expression="x0", value=2.5))

    def test_unsatisfiable_inequality_rejected(self) -> None:
        with pytest.raises(UnsupportedConstraintError, match="cannot be satisfied"):
            ConstraintPenalizer().penalize(Constraint.le("c", expression="x0 + x1", value=-2.0))


class TestPenalizerConfig:
    def test_default_penalty(self) -> None:
        assert ConstraintPenalizer().penalty == 10.0

    def test_penalty_validation(self) -> None:
        with pytest.raises(ValueError):
            ConstraintPenalizer(penalty=-1.0)
        with pytest.raises(ValueError):
            ConstraintPenalizer(penalty=0.0)
        with pytest.raises(ValueError):
            ConstraintPenalizer(penalty=float("nan"))


class TestPenaltyTermSerialization:
    def test_to_dict_round_trip(self) -> None:
        term = ConstraintPenalizer(penalty=2.0).penalize(
            Constraint.le("cap", expression="2*x0 + 3*x1", value=5.0)
        )
        data = term.to_dict()
        assert data["constraint"] == "cap"
        assert data["operator"] == "<="
        assert data["weight"] == 2.0
        assert data["slack_variables"] == [
            "cap_slack_0",
            "cap_slack_1",
            "cap_slack_2",
        ]
        assert "cap_slack_0,cap_slack_1" in data["quadratic"]
        assert "P = 2.0" in data["expression"]

    def test_declares_name_and_operator(self) -> None:
        term = ConstraintPenalizer().penalize(Constraint.ge("min", expression="x0", value=1.0))
        assert term.constraint == "min"
        assert term.operator in {">=", "=="}
