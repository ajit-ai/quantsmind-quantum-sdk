"""Deterministic validation helpers shared by the Data models."""

from __future__ import annotations

import math
from collections.abc import Sequence

from quantsmind.quantum.data.errors import DataValidationError

__all__ = [
    "check_finite",
    "check_nonempty_name",
    "check_nonnegative",
    "check_unique_names",
    "sorted_issues",
]


def check_finite(value: float, *, label: str) -> None:
    """Raise :class:`DataValidationError` when ``value`` is not finite."""
    try:
        finite = math.isfinite(float(value))
    except (TypeError, ValueError):
        finite = False
    if not finite:
        raise DataValidationError(f"{label} must be a finite number, got {value!r}")


def check_nonnegative(value: float, *, label: str) -> None:
    """Raise :class:`DataValidationError` when ``value`` is negative."""
    check_finite(value, label=label)
    if float(value) < 0.0:
        raise DataValidationError(f"{label} must be non-negative, got {value!r}")


def check_nonempty_name(name: str, *, label: str) -> None:
    """Raise :class:`DataValidationError` when ``name`` is empty or blank."""
    if not isinstance(name, str) or not name.strip():
        raise DataValidationError(f"{label} must be a non-empty string, got {name!r}")


def check_unique_names(names: Sequence[str], *, label: str) -> None:
    """Raise :class:`DataValidationError` when ``names`` contains duplicates."""
    seen: set[str] = set()
    for name in names:
        if name in seen:
            raise DataValidationError(f"duplicate {label} name {name!r}")
        seen.add(name)


def sorted_issues(issues: Sequence[str]) -> list[str]:
    """Return a deterministic (sorted, de-duplicated) issue list."""
    return sorted(set(issue for issue in issues if issue))
