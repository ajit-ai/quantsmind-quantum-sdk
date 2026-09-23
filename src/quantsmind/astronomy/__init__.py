"""Astronomy Package — Defines the astronomical systems domain model.

This package is part of the QuantsMind SDK (R0.1.0).
Foundational sky-calculation implementation (Phase 11): angular
separations, unit conversions, Keplerian orbits, parallax distances.
"""

from __future__ import annotations

from quantsmind.astronomy.sky import (
    ASTRONOMICAL_UNIT_M,
    GRAVITATIONAL_CONSTANT,
    LIGHT_YEAR_M,
    PARSEC_M,
    SOLAR_MASS_KG,
    angular_separation,
    au_to_m,
    circular_orbital_velocity,
    kepler_period,
    light_year_to_m,
    m_to_au,
    parallax_distance_pc,
    parsec_to_m,
)

__all__: list[str] = [
    "ASTRONOMICAL_UNIT_M",
    "GRAVITATIONAL_CONSTANT",
    "LIGHT_YEAR_M",
    "PARSEC_M",
    "SOLAR_MASS_KG",
    "angular_separation",
    "au_to_m",
    "circular_orbital_velocity",
    "kepler_period",
    "light_year_to_m",
    "m_to_au",
    "parallax_distance_pc",
    "parsec_to_m",
]
