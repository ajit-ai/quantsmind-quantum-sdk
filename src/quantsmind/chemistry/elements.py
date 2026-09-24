"""Chemical element and composition foundations.

A curated element table (IUPAC 2021 conventional atomic masses for the
covered elements), molecular-mass arithmetic over composition dicts, a
minimal flat-formula parser (no parentheses), and mole/mass/molarity
conversions. Deterministic and dependency-free.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = [
    "Element",
    "ELEMENTS",
    "element",
    "molar_mass",
    "parse_formula",
    "moles_from_mass",
    "mass_from_moles",
    "molarity",
]

#: Avogadro constant, exact by definition (1/mol).
AVOGADRO_CONSTANT = 6.02214076e23


@dataclass(frozen=True)
class Element:
    """A chemical element identity.

    Args:
        symbol: Element symbol (e.g. ``"O"``).
        name: Element name.
        atomic_number: Proton count.
        atomic_mass: Conventional atomic mass (u).
    """

    symbol: str
    name: str
    atomic_number: int
    atomic_mass: float


def _table() -> dict[str, Element]:
    rows = [
        ("H", "Hydrogen", 1, 1.008),
        ("He", "Helium", 2, 4.0026),
        ("Li", "Lithium", 3, 6.94),
        ("Be", "Beryllium", 4, 9.0122),
        ("B", "Boron", 5, 10.81),
        ("C", "Carbon", 6, 12.011),
        ("N", "Nitrogen", 7, 14.007),
        ("O", "Oxygen", 8, 15.999),
        ("F", "Fluorine", 9, 18.998),
        ("Ne", "Neon", 10, 20.180),
        ("Na", "Sodium", 11, 22.990),
        ("Mg", "Magnesium", 12, 24.305),
        ("Al", "Aluminium", 13, 26.982),
        ("Si", "Silicon", 14, 28.085),
        ("P", "Phosphorus", 15, 30.974),
        ("S", "Sulfur", 16, 32.06),
        ("Cl", "Chlorine", 17, 35.45),
        ("K", "Potassium", 19, 39.098),
        ("Ar", "Argon", 18, 39.948),
        ("Ca", "Calcium", 20, 40.078),
        ("Fe", "Iron", 26, 55.845),
        ("Cu", "Copper", 29, 63.546),
        ("Zn", "Zinc", 30, 65.38),
        ("Br", "Bromine", 35, 79.904),
        ("Ag", "Silver", 47, 107.87),
        ("I", "Iodine", 53, 126.90),
        ("Au", "Gold", 79, 196.97),
        ("Hg", "Mercury", 80, 200.59),
        ("Pb", "Lead", 82, 207.2),
    ]
    return {symbol: Element(symbol, name, number, mass) for symbol, name, number, mass in rows}


#: Curated element table by symbol.
ELEMENTS: dict[str, Element] = _table()

_FORMULA_TOKEN = re.compile(r"([A-Z][a-z]?)(\d*)")


def element(symbol: str) -> Element:
    """Look up an element by symbol (case-sensitive).

    Raises:
        KeyError: If the symbol is not in the curated table.
    """
    return ELEMENTS[symbol]


def molar_mass(composition: dict[str, int]) -> float:
    """Molecular mass (g/mol) of a ``{symbol: count}`` composition.

    Raises:
        KeyError: For unknown symbols.
        ValueError: For empty compositions or non-positive counts.
    """
    if not composition:
        raise ValueError("composition must not be empty")
    total = 0.0
    for symbol, count in composition.items():
        if count <= 0:
            raise ValueError(f"count for {symbol!r} must be positive, got {count!r}")
        total += ELEMENTS[symbol].atomic_mass * count
    return total


def parse_formula(formula: str) -> dict[str, int]:
    """Parse a flat chemical formula (e.g. ``"H2O"``) into a composition.

    Only bare element symbols with optional integer counts are supported;
    parentheses, charges, and hydrates are out of scope.

    Raises:
        ValueError: If the formula is empty or malformed.
        KeyError: For unknown element symbols.
    """
    if not formula or not formula[0].isupper():
        raise ValueError(f"malformed formula: {formula!r}")
    composition: dict[str, int] = {}
    position = 0
    for match in _FORMULA_TOKEN.finditer(formula):
        if match.start() != position:
            raise ValueError(f"malformed formula: {formula!r}")
        symbol, count = match.group(1), match.group(2)
        _ = ELEMENTS[symbol]
        composition[symbol] = composition.get(symbol, 0) + (int(count) if count else 1)
        position = match.end()
    if position != len(formula):
        raise ValueError(f"malformed formula: {formula!r}")
    return composition


def moles_from_mass(mass_g: float, molar_mass_value: float) -> float:
    """Moles from a sample mass (g) and molar mass (g/mol)."""
    if mass_g < 0.0:
        raise ValueError(f"mass must be non-negative, got {mass_g!r}")
    if molar_mass_value <= 0.0:
        raise ValueError(f"molar mass must be positive, got {molar_mass_value!r}")
    return mass_g / molar_mass_value


def mass_from_moles(moles: float, molar_mass_value: float) -> float:
    """Sample mass (g) from moles and molar mass (g/mol)."""
    if moles < 0.0:
        raise ValueError(f"moles must be non-negative, got {moles!r}")
    if molar_mass_value <= 0.0:
        raise ValueError(f"molar mass must be positive, got {molar_mass_value!r}")
    return moles * molar_mass_value


def molarity(moles: float, volume_liters: float) -> float:
    """Molar concentration (mol/L) from moles and solution volume (L)."""
    if moles < 0.0:
        raise ValueError(f"moles must be non-negative, got {moles!r}")
    if volume_liters <= 0.0:
        raise ValueError(f"volume must be positive, got {volume_liters!r}")
    return moles / volume_liters
