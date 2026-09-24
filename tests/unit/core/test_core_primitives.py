"""Unit tests for quantsmind.core primitives."""

from __future__ import annotations

from quantsmind.core import (
    Equation,
    Expression,
    ExpressionEngine,
    Formula,
    MathObject,
    Parameter,
    Variable,
)


class TestVariables:
    def test_variable(self) -> None:
        var = Variable("x", 2.0)
        assert var.name == "x"
        assert var.value == 2.0

    def test_parameter(self) -> None:
        param = Parameter("p", 3.0)
        assert param.name == "p"
        assert param.value == 3.0


class TestExpressions:
    def test_evaluate_kwargs(self) -> None:
        expr = Expression("sum", ["x", 1], ["+"])
        assert expr.evaluate(x=2) == 3.0

    def test_formula_delegates(self) -> None:
        formula = Formula("double", Expression("sum", ["x", 1], ["+"]))
        assert formula.evaluate(x=3) == 4.0

    def test_equation_check(self) -> None:
        left = Expression("sum", ["x", 1], ["+"])
        right = Expression("const", [4])
        equation = Equation("eq", left, right)
        assert equation.check_solution(x=3) is True
        assert equation.check_solution(x=0) is False


class TestEngine:
    def test_parse_and_evaluate(self) -> None:
        engine = ExpressionEngine()
        expr = engine.parse_expression("x + 1")
        assert engine.evaluate(expr, x=2) == 3.0

    def test_math_object_base(self) -> None:
        class Concrete(MathObject):
            def evaluate(self, **kwargs: object) -> float:
                return 1.0

        obj = Concrete("m")
        assert isinstance(obj, MathObject)
        assert obj.name == "m"
        assert obj.evaluate() == 1.0
