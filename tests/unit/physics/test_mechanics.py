"""Unit tests for quantsmind.physics.mechanics."""

from __future__ import annotations

import pytest

from quantsmind.physics import (
    centripetal_acceleration,
    flight_time,
    heat_conduction,
    kinetic_energy,
    mass_energy,
    momentum,
    newton_second_law,
    potential_energy,
    projectile_max_height,
    projectile_range,
    shm_period,
    wave_energy,
    wave_speed,
)


class TestProjectile:
    def test_range_45_degrees(self) -> None:
        assert projectile_range(10.0, 45.0) == pytest.approx(10.197162129779283)

    def test_range_zero_angle(self) -> None:
        assert projectile_range(10.0, 0.0) == pytest.approx(0.0)

    def test_max_height(self) -> None:
        assert projectile_max_height(10.0, 45.0) == pytest.approx(2.549290532444821)

    def test_flight_time(self) -> None:
        assert flight_time(10.0, 45.0) == pytest.approx(1.4420964981651176)

    def test_invalid_angle(self) -> None:
        with pytest.raises(ValueError):
            projectile_range(10.0, 120.0)

    def test_negative_speed(self) -> None:
        with pytest.raises(ValueError):
            projectile_range(-1.0, 45.0)


class TestEnergy:
    def test_kinetic(self) -> None:
        assert kinetic_energy(2.0, 3.0) == pytest.approx(9.0)

    def test_potential(self) -> None:
        assert potential_energy(2.0, 5.0) == pytest.approx(98.0665)

    def test_momentum_and_force(self) -> None:
        assert momentum(2.0, 3.0) == pytest.approx(6.0)
        assert newton_second_law(2.0, 9.80665) == pytest.approx(19.6133)

    def test_wave_relations(self) -> None:
        assert wave_speed(440.0, 0.781) == pytest.approx(343.64)
        assert wave_energy(5e14) == pytest.approx(3.313035075e-19)

    def test_mass_energy(self) -> None:
        assert mass_energy(1.0) == pytest.approx(8.987551787e16)

    def test_negative_mass(self) -> None:
        with pytest.raises(ValueError):
            kinetic_energy(-1.0, 3.0)

    def test_heat_conduction(self) -> None:
        assert heat_conduction(0.04, 10.0, 20.0, 0.20) == pytest.approx(40.0)
        with pytest.raises(ValueError):
            heat_conduction(0.04, 10.0, 20.0, 0.0)

    def test_rotation_and_oscillation(self) -> None:
        assert centripetal_acceleration(2.0, 3.0) == pytest.approx(12.0)
        assert shm_period(1.0, 4.0) == pytest.approx(3.14159265)
        with pytest.raises(ValueError):
            shm_period(0.0, 4.0)
