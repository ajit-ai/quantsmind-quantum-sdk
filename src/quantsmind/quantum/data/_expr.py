"""Deterministic expression-string helpers for the Data Intelligence layer.

The Data layer produces **symbolic string** objectives and constraints that
the existing QMQ-02 expression parser understands (``parse_expression`` from
:mod:`quantsmind.quantum.optimization.expression`).  This module owns the
two canonical mappings all Data code depends on:

* the decision-variable naming conventions derived from the deterministic
  feature and record ordering (``x0, x1, ...`` for feature selection and
  ``z{record}_{cluster}`` for clustering), and
* the deterministic number formatting used inside generated expressions.

The naming conventions are the single source of truth for the
feature/record -> domain variable -> QMQ variable -> QUBO index mapping.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

__all__ = [
    "variable_name",
    "variable_names",
    "cluster_variable_name",
    "cluster_variable_names",
    "fmt_number",
    "linear_string",
    "quadratic_string",
]

_NUMBER_PATTERN = re.compile(r"\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|\.\d+")


def variable_name(index: int) -> str:
    """Return the decision-variable name of the ``index``-th feature."""
    return f"x{index}"


def variable_names(size: int) -> list[str]:
    """Return the decision-variable names ``x0 .. x{n-1}`` for ``n`` features."""
    return [variable_name(index) for index in range(size)]


def cluster_variable_name(record_index: int, cluster_index: int) -> str:
    """Return the clustering assignment-variable name ``z{record}_{cluster}``."""
    return f"z{record_index}_{cluster_index}"


def cluster_variable_names(num_records: int, k: int) -> list[str]:
    """Return clustering assignment variables in record-major order.

    The deterministic order is ``z0_0, z0_1, ..., z0_{k-1}, z1_0, ...`` so that
    the ``record in exactly one cluster`` family of constraints touches
    contiguous indices.
    """
    return [
        cluster_variable_name(record_index, cluster_index)
        for record_index in range(num_records)
        for cluster_index in range(k)
    ]


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
    """Build a symbolic linear expression ``c0*v0 + c1*v1 + ...``.

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
    a zero coefficient are dropped.
    """
    parts: list[str] = []
    for left, right, coefficient in terms:
        if coefficient == 0.0:
            continue
        parts.append(f"{fmt_number(coefficient)}*{left}*{right}")
    return " + ".join(parts) if parts else "0"
