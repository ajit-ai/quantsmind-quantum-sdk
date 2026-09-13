"""Deterministic expression-string helpers for the Finance layer.

The Finance layer produces **symbolic string** objectives and constraints
that the existing QMQ-02 expression parser understands (``parse_expression``
from :mod:`quantsmind.quantum.optimization.expression`).  This module owns
the two canonical mappings all Finance code depends on:

* the decision-variable naming convention ``x0, x1, ...`` derived from the
  deterministic asset ordering, and
* the number formatting used inside generated expressions (lexer-compatible,
  deterministic).

The variable naming convention is the single source of truth for the
asset -> domain variable -> mathematical variable -> binary/QUBO index
mapping that QMQ-08 will build on.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

__all__ = [
    "variable_name",
    "variable_names",
    "fmt_number",
    "linear_string",
    "quadratic_string",
]

_NUMBER_PATTERN = re.compile(r"\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|\.\d+")


def variable_name(index: int) -> str:
    """Return the decision-variable name of the ``index``-th asset."""
    return f"x{index}"


def variable_names(size: int) -> list[str]:
    """Return the decision-variable names ``x0 .. x{n-1}`` for ``n`` assets."""
    return [variable_name(index) for index in range(size)]


def fmt_number(value: float) -> str:
    """Format a float as a token the expression lexer accepts (deterministic).

    Raises:
        ValueError: If the value is not finite (never expected after model
            validation).
    """
    text = repr(float(value))
    if not _NUMBER_PATTERN.fullmatch(text.lstrip("-")):
        raise ValueError(f"value {value!r} is not a lexer-compatible number")
    return text


def linear_string(coefficients: Sequence[float], variables: Sequence[str]) -> str:
    """Build a symbolic linear expression ``c0*x0 + c1*x1 + ...``.

    Zero coefficients are dropped; an all-zero (or empty) expression is the
    literal ``"0"``.
    """
    parts: list[str] = []
    for variable, coefficient in zip(variables, coefficients, strict=True):
        if coefficient == 0.0:
            continue
        parts.append(f"{fmt_number(coefficient)}*{variable}")
    return " + ".join(parts) if parts else "0"


def quadratic_string(terms: Sequence[tuple[str, str, float]]) -> str:
    """Build a symbolic quadratic expression ``c*(v1*v2) + ...`` over monomials.

    Each term is ``(left_variable, right_variable, coefficient)``; terms with
    a zero coefficient are dropped.  Pairing symmetry of a covariance matrix
    is preserved by emitting every ordered pair.
    """
    parts: list[str] = []
    for left, right, coefficient in terms:
        if coefficient == 0.0:
            continue
        parts.append(f"{fmt_number(coefficient)}*{left}*{right}")
    return " + ".join(parts) if parts else "0"
