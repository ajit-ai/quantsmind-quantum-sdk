"""Unit tests for quantsmind.astronomy.sky."""

from __future__ import annotations

import pytest

from quantsmind.astronomy import (
    absolute_magnitude,
    angular_separation,
    au_to_m,
    circular_orbital_velocity,
    distance_modulus,
    kepler_period,
    light_year_to_m,
    m_to_au,
    parallax_distance_pc,
    parsec_to_m,
)


class TestAngles:
    def test_quarter_sky(self) -> None:
        assert angular_separation(0.0, 0.0, 90.0, 0.0) == pytest.approx(90.0)

    def test_same_point(self) -> None:
        assert angular_separation(10.0, 20.0, 10.0, 20.0) == pytest.approx(0.0)


class TestUnits:
    def test_au_roundtrip(self) -> None:
        assert au_to_m(1.0) == pytest.approx(1.495978707e11)
        assert m_to_au(1.495978707e11) == pytest.approx(1.0)

    def test_light_year_and_parsec(self) -> None:
        assert light_year_to_m(1.0) == pytest.approx(9.4607304725808e15)
        assert parsec_to_m(1.0) == pytest.approx(3.08567758149137e16)

    def test_negative_rejected(self) -> None:
        with pytest.raises(ValueError):
            au_to_m(-1.0)


class TestOrbits:
    def test_earth_year(self) -> None:
        period = kepler_period(1.495978707e11, 1.98847e30)
        assert period == pytest.approx(31557719.0, rel=1e-3)

    def test_parallax(self) -> None:
        assert parallax_distance_pc(0.5) == pytest.approx(2.0)
        with pytest.raises(ValueError):
            parallax_distance_pc(0.0)

    def test_circular_velocity(self) -> None:
        velocity = circular_orbital_velocity(1.495978707e11, 1.98847e30)
        assert velocity == pytest.approx(29785.0, rel=1e-3)


class TestMagnitudes:
    def test_ten_parsecs(self) -> None:
        assert distance_modulus(10.0) == pytest.approx(0.0)
        assert absolute_magnitude(5.0, 10.0) == pytest.approx(5.0)

    def test_invalid_distance(self) -> None:
        with pytest.raises(ValueError):
            distance_modulus(0.0)
