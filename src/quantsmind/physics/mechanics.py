"""Classical-mechanics foundations.

Small, deterministic, dependency-free primitives: projectile kinematics,
Newtonian dynamics, mechanical energy, and basic wave relations. All
quantities are plain floats in SI units; constants are exact defined
values (standard gravity, speed of light, Planck constant).
"""

from __future__ import annotations

import math

__all__ = [
    "STANDARD_GRAVITY",
    "SPEED_OF_LIGHT",
    "PLANCK_CONSTANT",
    "projectile_range",
    "projectile_max_height",
    "flight_time",
    "kinetic_energy",
    "potential_energy",
    "momentum",
    "newton_second_law",
    "wave_speed",
    "wave_energy",
    "mass_energy",
    "heat_conduction",
    "centripetal_acceleration",
    "shm_period",
]

#: Standard gravity on Earth, exact by definition (m/s^2).
STANDARD_GRAVITY = 9.80665
#: Speed of light in vacuum, exact by definition (m/s).
SPEED_OF_LIGHT = 299792458.0
#: Planck constant, exact by definition (J*s).
PLANCK_CONSTANT = 6.62607015e-34


def _require_non_negative(name: str, value: float) -> float:
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be a finite non-negative number, got {value!r}")
    return float(value)


def projectile_range(
    initial_speed: float, angle_degrees: float, g: float = STANDARD_GRAVITY
) -> float:
    """Horizontal range of a projectile launched over flat ground (m)."""
    _require_non_negative("initial_speed", initial_speed)
    if not 0.0 <= angle_degrees <= 90.0:
        raise ValueError(f"angle must be within [0, 90] degrees, got {angle_degrees!r}")
    return initial_speed**2 * math.sin(math.radians(2.0 * angle_degrees)) / g


def projectile_max_height(
    initial_speed: float, angle_degrees: float, g: float = STANDARD_GRAVITY
) -> float:
    """Maximum height of a projectile trajectory (m)."""
    _require_non_negative("initial_speed", initial_speed)
    if not 0.0 <= angle_degrees <= 90.0:
        raise ValueError(f"angle must be within [0, 90] degrees, got {angle_degrees!r}")
    vertical = initial_speed * math.sin(math.radians(angle_degrees))
    return vertical**2 / (2.0 * g)


def flight_time(
    initial_speed: float, angle_degrees: float, g: float = STANDARD_GRAVITY
) -> float:
    """Total time of flight of a projectile (s)."""
    _require_non_negative("initial_speed", initial_speed)
    if not 0.0 <= angle_degrees <= 90.0:
        raise ValueError(f"angle must be within [0, 90] degrees, got {angle_degrees!r}")
    return 2.0 * initial_speed * math.sin(math.radians(angle_degrees)) / g


def kinetic_energy(mass: float, velocity: float) -> float:
    """Kinetic energy ``m*v^2/2`` (J)."""
    _require_non_negative("mass", mass)
    return 0.5 * mass * float(velocity) ** 2


def potential_energy(
    mass: float, height: float, g: float = STANDARD_GRAVITY
) -> float:
    """Gravitational potential energy ``m*g*h`` (J)."""
    _require_non_negative("mass", mass)
    return mass * g * float(height)


def momentum(mass: float, velocity: float) -> float:
    """Linear momentum ``m*v`` (kg*m/s)."""
    _require_non_negative("mass", mass)
    return mass * float(velocity)


def newton_second_law(mass: float, acceleration: float) -> float:
    """Force ``F = m*a`` (N)."""
    _require_non_negative("mass", mass)
    return mass * float(acceleration)


def wave_speed(frequency: float, wavelength: float) -> float:
    """Wave speed ``v = f*lambda`` (m/s)."""
    _require_non_negative("frequency", frequency)
    _require_non_negative("wavelength", wavelength)
    return frequency * wavelength


def wave_energy(frequency: float, h: float = PLANCK_CONSTANT) -> float:
    """Photon energy ``E = h*f`` (J)."""
    _require_non_negative("frequency", frequency)
    return h * frequency


def mass_energy(mass: float, c: float = SPEED_OF_LIGHT) -> float:
    """Mass-energy equivalence ``E = m*c^2`` (J)."""
    _require_non_negative("mass", mass)
    return mass * c**2


def heat_conduction(
    conductivity: float, area: float, delta_t: float, thickness: float
) -> float:
    """Steady-state conductive heat rate ``Q = k*A*dT/d`` (W)."""
    _require_non_negative("conductivity", conductivity)
    _require_non_negative("area", area)
    if thickness <= 0.0:
        raise ValueError(f"thickness must be positive, got {thickness!r}")
    return conductivity * area * float(delta_t) / thickness


def centripetal_acceleration(angular_velocity: float, radius: float) -> float:
    """Centripetal acceleration ``a = w^2 * r`` (m/s^2)."""
    if radius < 0.0:
        raise ValueError(f"radius must be non-negative, got {radius!r}")
    return float(angular_velocity) ** 2 * radius


def shm_period(mass: float, spring_constant: float) -> float:
    """Period of a mass-spring oscillator ``T = 2*pi*sqrt(m/k)`` (s)."""
    if mass <= 0.0:
        raise ValueError(f"mass must be positive, got {mass!r}")
    if spring_constant <= 0.0:
        raise ValueError(f"spring constant must be positive, got {spring_constant!r}")
    return 2.0 * math.pi * math.sqrt(mass / spring_constant)
