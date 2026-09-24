"""Core expressions: parse, evaluate, and check an equation.

Feature: expression machinery from ``quantsmind.core``.
Purpose: show the shared vocabulary other layers build on.
Input: the string "x + 1" with x = 2, equation against 4.
Processing: parse -> evaluate -> solution check.
Output: 3.0 and a satisfied equation.
Meaning: names, terms, and assignments compose predictably.

Run from the repository root::

    python examples/core/expressions.py
"""

from __future__ import annotations

from quantsmind.core import Equation, Expression, ExpressionEngine


def main() -> None:
    engine = ExpressionEngine()
    expr = engine.parse_expression("x + 1")
    print(f"value: {engine.evaluate(expr, x=2)}")
    equation = Equation("eq", expr, Expression("const", [4]))
    print(f"satisfied at x=3: {equation.check_solution(x=3)}")


if __name__ == "__main__":
    main()
