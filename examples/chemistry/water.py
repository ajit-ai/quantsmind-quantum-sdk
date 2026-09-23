"""Water chemistry: formula parsing, molar mass, and solution prep.

Feature: element lookup, formula parsing, molar-mass arithmetic.
Purpose: show deterministic composition math from ``quantsmind.chemistry``.
Input: formula "H2O", a 36.03 g sample, a 2 L flask.
Processing: parse -> molar mass -> moles -> molarity.
Output: 18.015 g/mol, 2.0 mol, 1.0 mol/L solution.
Meaning: the parsed composition drives every downstream quantity.

Run from the repository root::

    python examples/chemistry/water.py
"""

from __future__ import annotations

from quantsmind.chemistry import (
    mass_from_moles,
    molar_mass,
    molarity,
    moles_from_mass,
    parse_formula,
)


def main() -> None:
    composition = parse_formula("H2O")
    print(f"composition: {composition}")
    mass = molar_mass(composition)
    print(f"molar mass: {mass:.3f} g/mol")
    sample_g = 2.0 * mass
    moles = moles_from_mass(sample_g, mass)
    print(f"{sample_g:.3f} g -> {moles:.3f} mol")
    print(f"in 2 L: {molarity(moles, 2.0):.3f} mol/L")
    print(f"1 mol weighs: {mass_from_moles(1.0, mass):.3f} g")


if __name__ == "__main__":
    main()
