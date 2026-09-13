"""Numeric distance and similarity primitives of the Data Intelligence layer.

All functions accept any finite numeric sequence (``list[float]`` or
:class:`FeatureVector.to_list`) and are deterministic and strict about
dimension mismatches and non-finite inputs.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from quantsmind.quantum.data.errors import DataValidationError

__all__ = [
    "euclidean_distance",
    "squared_euclidean_distance",
    "weighted_squared_euclidean_distance",
    "similarity_from_distance",
]


def euclidean_distance(left: Sequence[float], right: Sequence[float]) -> float:
    """Return the Euclidean distance between two equal-length vectors."""
    return math.sqrt(squared_euclidean_distance(left, right))


def squared_euclidean_distance(left: Sequence[float], right: Sequence[float]) -> float:
    """Return the squared Euclidean distance between two vectors."""
    left_values = _coerce(left, "left")
    right_values = _coerce(right, "right")
    _check_dimensions(left_values, right_values)
    return float(sum((a - b) ** 2.0 for a, b in zip(left_values, right_values, strict=True)))


def weighted_squared_euclidean_distance(
    left: Sequence[float],
    right: Sequence[float],
    weights: Sequence[float],
) -> float:
    """Return the squared Euclidean distance with per-dimension weights."""
    left_values = _coerce(left, "left")
    right_values = _coerce(right, "right")
    weight_values = _coerce(weights, "weights")
    _check_dimensions(left_values, right_values)
    _check_dimensions(left_values, weight_values)
    for weight in weight_values:
        if weight < 0.0:
            raise DataValidationError("distance weights must be non-negative")
    return float(
        sum(
            weight * (a - b) ** 2.0
            for a, b, weight in zip(left_values, right_values, weight_values, strict=True)
        )
    )


def similarity_from_distance(distance: float, *, sigma: float = 1.0) -> float:
    """Return the Gaussian similarity ``exp(-distance^2 / (2 sigma^2))``.

    Args:
        distance: A non-negative distance.
        sigma: Positive kernel width.

    Returns:
        A value in ``(0, 1]``; identical vectors give ``1.0``.
    """
    from quantsmind.quantum.data._validation import check_finite, check_nonnegative

    check_finite(distance, label="distance")
    check_nonnegative(distance, label="distance")
    check_finite(sigma, label="sigma")
    if float(sigma) <= 0.0:
        raise DataValidationError("sigma must be a positive number")
    return math.exp(-(float(distance) ** 2.0) / (2.0 * float(sigma) ** 2.0))


def _coerce(values: Sequence[float], label: str) -> tuple[float, ...]:
    try:
        numbers = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise DataValidationError(f"{label} must be a sequence of finite numbers") from exc
    if not numbers:
        raise DataValidationError(f"{label} must contain at least one value")
    for value in numbers:
        if not math.isfinite(value):
            raise DataValidationError(f"{label} must contain only finite numbers")
    return numbers


def _check_dimensions(left: Sequence[float], right: Sequence[float]) -> None:
    if len(left) != len(right):
        raise DataValidationError(f"dimension mismatch: {len(left)} vs {len(right)}")
