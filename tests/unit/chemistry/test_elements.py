"""Unit tests for quantsmind.chemistry.elements."""

from __future__ import annotations

import pytest

from quantsmind.chemistry import (
    element,
    mass_from_moles,
    molar_mass,
    molarity,
    moles_from_mass,
    parse_formula,
)


class TestElements:
    def test_water(self) -> None:
        assert element("O").atomic_number == 8
        assert molar_mass({"H": 2, "O": 1}) == pytest.approx(18.015)

    def test_glucose(self) -> None:
        assert molar_mass(parse_formula("C6H12O6")) == pytest.approx(180.156)

    def test_parse_roundtrip(self) -> None:
        assert parse_formula("H2O") == {"H": 2, "O": 1}
        assert parse_formula("NaCl") == {"Na": 1, "Cl": 1}

    def test_unknown_symbol(self) -> None:
        with pytest.raises(KeyError):
            element("Xx")

    def test_malformed_formula(self) -> None:
        with pytest.raises(ValueError):
            parse_formula("h2o")
        with pytest.raises(ValueError):
            parse_formula("")

    def test_empty_composition(self) -> None:
        with pytest.raises(ValueError):
            molar_mass({})


class TestConversions:
    def test_mole_roundtrip(self) -> None:
        assert moles_from_mass(18.015, 18.015) == pytest.approx(1.0)
        assert mass_from_moles(2.0, 18.015) == pytest.approx(36.03)

    def test_molarity(self) -> None:
        assert molarity(0.5, 2.0) == pytest.approx(0.25)

    def test_invalid_inputs(self) -> None:
        with pytest.raises(ValueError):
            moles_from_mass(-1.0, 18.015)
        with pytest.raises(ValueError):
            molarity(1.0, 0.0)
