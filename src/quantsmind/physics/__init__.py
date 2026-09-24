"""Physics Package — Defines the domain model for physical systems (particles, fields, forces,
dynamics) built on the simulation and math layers.

This package is part of the QuantsMind SDK (R0.1.0).
Foundational classical-mechanics implementation (Phase 11): deterministic,
dependency-free primitives with SI float quantities.
"""

from __future__ import annotations

from quantsmind.physics.mechanics import (
    PLANCK_CONSTANT,
    SPEED_OF_LIGHT,
    STANDARD_GRAVITY,
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

__all__: list[str] = [
    "STANDARD_GRAVITY",
    "SPEED_OF_LIGHT",
    "PLANCK_CONSTANT",
    "projectile_range",
    "projectile_max_height",
    "centripetal_acceleration",
    "flight_time",
    "heat_conduction",
    "kinetic_energy",
    "potential_energy",
    "momentum",
    "newton_second_law",
    "wave_speed",
    "wave_energy",
    "mass_energy",
    "shm_period",
]
