"""Deterministic expression-string helpers for the AI/ML Intelligence layer.

The ML layer produces **symbolic string** objectives and constraints that the
existing QMQ-02 expression parser understands (``parse_expression`` from
:mod:`quantsmind.quantum.optimization.expression`).  This module owns the
decision-variable naming conventions derived from the deterministic feature,
candidate, record and hyperparameter ordering, and the deterministic number
formatting used inside generated expressions.

Naming conventions (single source of truth):

* ``w{feature_index}``   — binary coefficients of the linear least-squares
  fitting problems (classification / regression),
* ``s{candidate_index}`` — one-hot model-selection variables,
* ``h{param_index}_{choice_index}`` — one-hot hyperparameter-choice variables,
* delegated (feature selection / clustering) variables follow the Data
  layer conventions (``x<i>`` / ``z{record}_{cluster}``).
"""

from __future__ import annotations

import re
from collections.abc import Sequence

__all__ = [
    "coefficient_variable_name",
    "coefficient_variable_names",
    "selection_variable_name",
    "selection_variable_names",
    "hyperparameter_variable_name",
    "hyperparameter_variable_names",
    "fmt_number",
    "linear_string",
    "quadratic_string",
]

_NUMBER_PATTERN = re.compile(r"\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|\.\d+")


def coefficient_variable_name(index: int) -> str:
    """Return the decision-variable name ``w{index}`` (fitting coefficient)."""
    return f"w{index}"


def coefficient_variable_names(size: int) -> list[str]:
    """Return the fitting variable names ``w0 .. w{n-1}``."""
    return [coefficient_variable_name(index) for index in range(size)]


def selection_variable_name(index: int) -> str:
    """Return the model-selection variable name ``s{index}``."""
    return f"s{index}"


def selection_variable_names(size: int) -> list[str]:
    """Return the model-selection variable names ``s0 .. s{n-1}``."""
    return [selection_variable_name(index) for index in range(size)]


def hyperparameter_variable_name(param_index: int, choice_index: int) -> str:
    """Return the hyperparameter variable name ``h{param}_{choice}``."""
    return f"h{param_index}_{choice_index}"


def hyperparameter_variable_names(choice_counts: Sequence[int]) -> list[str]:
    """Return hyperparameter variables in parameter-major order.

    ``choice_counts[c]`` is the number of choices of the ``c``-th parameter;
    the deterministic order is ``h0_0, h0_1, ..., h1_0, ...`` so the
    ``exactly one choice per parameter`` constraints touch contiguous indices.
    """
    names: list[str] = []
    for param_index, count in enumerate(choice_counts):
        for choice_index in range(count):
            names.append(hyperparameter_variable_name(param_index, choice_index))
    return names


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
