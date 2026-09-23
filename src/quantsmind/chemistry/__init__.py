"""Chemistry Package — Defines the molecular/chemical systems domain model.

This package is part of the QuantsMind SDK (R0.1.0).
Foundational element/composition implementation (Phase 11): curated
element table, molar-mass arithmetic, and mole/molarity conversions.
"""

from __future__ import annotations

from quantsmind.chemistry.elements import (
    AVOGADRO_CONSTANT,
    ELEMENTS,
    Element,
    element,
    mass_from_moles,
    molar_mass,
    molarity,
    moles_from_mass,
    parse_formula,
)

__all__: list[str] = [
    "AVOGADRO_CONSTANT",
    "ELEMENTS",
    "Element",
    "element",
    "molar_mass",
    "parse_formula",
    "moles_from_mass",
    "mass_from_moles",
    "molarity",
]
