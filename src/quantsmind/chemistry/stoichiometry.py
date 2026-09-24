"""Stoichiometric calculations over composition dicts.

Limiting-reactant analysis and theoretical yields for reactions written
as ``{species: stoichiometric_coefficient}`` with available moles.
Deterministic and dependency-free.
"""

from __future__ import annotations

__all__ = [
    "limiting_reactant",
    "theoretical_yield_moles",
]


def limiting_reactant(
    stoichiometry: dict[str, float], available_moles: dict[str, float]
) -> tuple[str, float]:
    """Identify the limiting reactant and the reaction extent (mol).

    Args:
        stoichiometry: Species -> stoichiometric coefficient (> 0).
        available_moles: Species -> available moles (>= 0).

    Returns:
        ``(species, extent)`` with the smallest ``available / coeff``.

    Raises:
        ValueError: For empty inputs, non-positive coefficients,
            negative availability, or missing species.
    """
    if not stoichiometry:
        raise ValueError("stoichiometry must not be empty")
    limiting: str | None = None
    extent = float("inf")
    for species, coeff in stoichiometry.items():
        if coeff <= 0.0:
            raise ValueError(f"coefficient for {species!r} must be positive")
        if species not in available_moles:
            raise ValueError(f"no availability given for {species!r}")
        available = available_moles[species]
        if available < 0.0:
            raise ValueError(f"availability for {species!r} must be non-negative")
        candidate = available / coeff
        if candidate < extent:
            limiting, extent = species, candidate
    assert limiting is not None
    return limiting, extent


def theoretical_yield_moles(
    stoichiometry: dict[str, float],
    available_moles: dict[str, float],
    product_coeff: float = 1.0,
) -> float:
    """Maximum product moles at full conversion of the limiting reactant."""
    if product_coeff <= 0.0:
        raise ValueError(f"product coefficient must be positive, got {product_coeff!r}")
    _, extent = limiting_reactant(stoichiometry, available_moles)
    return extent * product_coeff
