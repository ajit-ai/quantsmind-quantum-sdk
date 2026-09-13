"""Tests for the QMQ-02 symbolic expression model."""

from __future__ import annotations

import pytest

from quantsmind.quantum.optimization.expression import (
    Constant,
    ExpressionError,
    ExpressionParseError,
    VariableExpression,
    coefficient,
    coerce_expression,
    const,
    evaluate_expression,
    parse_expression,
    var,
)


class TestParseAndEvaluate:
    def test_simple_linear_evaluates(self) -> None:
        expr = parse_expression("3*x0 + 2*x1 - 1")
        assert expr.evaluate({"x0": 2, "x1": 3}) == 11.0

    def test_parens_and_precedence(self) -> None:
        expr = parse_expression("(x + 1) * 3")
        assert expr.evaluate({"x": 2}) == 9.0

    def test_unary_minus(self) -> None:
        assert parse_expression("-x + 5").evaluate({"x": 3}) == 2.0

    def test_power_with_star_star(self) -> None:
        assert parse_expression("x**2").evaluate({"x": 3}) == 9.0

    def test_power_with_caret(self) -> None:
        assert parse_expression("x^3").evaluate({"x": 2}) == 8.0

    def test_float_literals(self) -> None:
        assert parse_expression("0.5*x + 1e2").evaluate({"x": 2}) == 101.0

    def test_positivity_of_zero_exponent(self) -> None:
        assert parse_expression("x**0").evaluate({"x": 5}) == 1.0

    def test_missing_variable_raises(self) -> None:
        with pytest.raises(KeyError, match="missing variable"):
            parse_expression("x + 1").evaluate({"y": 1})


class TestParseErrors:
    @pytest.mark.parametrize(
        "text",
        [
            "2x + 1",
            "x <= 5",
            "x@y",
            "",
            "  ",
            "(x + 1",
            "x +",
            "x**1.5",
            "x**-1",
            "x**33",
        ],
    )
    def test_invalid_expressions_rejected(self, text: str) -> None:
        with pytest.raises(ExpressionParseError):
            parse_expression(text)

    def test_invalid_variable_name(self) -> None:
        with pytest.raises(ExpressionError):
            VariableExpression("1x")
        with pytest.raises(ExpressionError):
            VariableExpression("x y")

    def test_nonfinite_constant(self) -> None:
        with pytest.raises(ExpressionError):
            Constant(float("nan"))


class TestExpand:
    def test_linear_and_quadratic(self) -> None:
        expr = parse_expression("2*x*x + 3*x + 4*x*y")
        assert expr.expand() == {
            ("x", "x"): 2.0,
            ("x",): 3.0,
            ("x", "y"): 4.0,
        }

    def test_constant_key(self) -> None:
        assert parse_expression("x - 5").expand()[()] == -5.0

    def test_product_duplicate_preserved(self) -> None:
        assert parse_expression("x*y*x").expand() == {("x", "x", "y"): 1.0}


class TestHelpersAndCoercion:
    def test_var_const_coefficient(self) -> None:
        expr = coefficient(2.0, var("x")) + const(1.0)
        assert expr.evaluate({"x": 3}) == 7.0

    def test_operator_overloads(self) -> None:
        expr = 2 * var("x") + 1 - var("y")
        assert expr.evaluate({"x": 2, "y": 1}) == 4.0

    def test_coerce_numbers(self) -> None:
        assert coerce_expression(3).evaluate({}) == 3.0
        assert coerce_expression(True).evaluate({}) == 1.0

    def test_coerce_expression_passthrough(self) -> None:
        node = var("a")
        assert coerce_expression(node) is node

    def test_coerce_callable_rejected(self) -> None:
        with pytest.raises(ExpressionError, match="callable"):
            coerce_expression(lambda v: 1)  # type: ignore[arg-type]

    def test_coerce_unsupported_rejected(self) -> None:
        with pytest.raises(ExpressionError):
            coerce_expression(object())  # type: ignore[arg-type]

    def test_evaluate_expression_variants(self) -> None:
        assert evaluate_expression("2*x", {"x": 3}) == 6.0
        assert evaluate_expression(4.0, {}) == 4.0
        assert evaluate_expression(var("a"), {"a": 5}) == 5.0
        assert evaluate_expression(lambda v: v["a"] * 2, {"a": 5}) == 10.0

    def test_variables_property(self) -> None:
        assert parse_expression("b + a + b").variables == ("b", "a")
