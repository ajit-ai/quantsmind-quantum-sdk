"""Foundational cosmology calculations.

Hubble-law velocities, scale-factor/redshift relations, Hubble distance
and time, relativistic Doppler redshift, and component density scalings.
Linear (low-redshift) approximations are flagged where used; all
quantities are plain floats, deterministic and dependency-free.
"""

from __future__ import annotations

import math

__all__ = [
    "HUBBLE_CONSTANT_DEFAULT",
    "KM_PER_MPC",
    "SPEED_OF_LIGHT",
    "SECONDS_PER_GYR",
    "hubble_velocity",
    "scale_factor",
    "redshift_from_scale",
    "hubble_distance_mpc",
    "hubble_time_gyr",
    "doppler_redshift",
    "density_scaling",
    "luminosity_distance_linear_mpc",
]

#: Default Hubble constant H0 (km/s/Mpc); Planck-rough value for examples.
HUBBLE_CONSTANT_DEFAULT = 70.0
#: Kilometers per megaparsec, exact from the AU-derived parsec.
KM_PER_MPC = 3.08567758149137e19
#: Speed of light in vacuum, exact (m/s).
SPEED_OF_LIGHT = 299792458.0
#: Seconds per gigayear (Julian year).
SECONDS_PER_GYR = 1e9 * 365.25 * 86400.0


def hubble_velocity(
    distance_mpc: float, h0: float = HUBBLE_CONSTANT_DEFAULT
) -> float:
    """Recession velocity ``v = H0 * d`` (km/s)."""
    if distance_mpc < 0.0:
        raise ValueError(f"distance must be non-negative, got {distance_mpc!r}")
    if h0 <= 0.0:
        raise ValueError(f"H0 must be positive, got {h0!r}")
    return h0 * distance_mpc


def scale_factor(redshift: float) -> float:
    """Scale factor ``a = 1 / (1 + z)``."""
    if redshift < 0.0:
        raise ValueError(f"redshift must be non-negative, got {redshift!r}")
    return 1.0 / (1.0 + redshift)


def redshift_from_scale(scale: float) -> float:
    """Redshift ``z = 1/a - 1``."""
    if scale <= 0.0:
        raise ValueError(f"scale factor must be positive, got {scale!r}")
    return 1.0 / scale - 1.0


def _h0_per_second(h0: float) -> float:
    """Hubble constant in s^-1."""
    if h0 <= 0.0:
        raise ValueError(f"H0 must be positive, got {h0!r}")
    meters_per_mpc = KM_PER_MPC * 1000.0
    return (h0 * 1000.0) / meters_per_mpc


def hubble_distance_mpc(h0: float = HUBBLE_CONSTANT_DEFAULT) -> float:
    """Hubble distance ``c / H0`` (Mpc)."""
    meters_per_mpc = KM_PER_MPC * 1000.0
    return (SPEED_OF_LIGHT / _h0_per_second(h0)) / meters_per_mpc


def hubble_time_gyr(h0: float = HUBBLE_CONSTANT_DEFAULT) -> float:
    """Hubble time ``1 / H0`` (Gyr)."""
    return (1.0 / _h0_per_second(h0)) / SECONDS_PER_GYR


def doppler_redshift(velocity_ms: float, c: float = SPEED_OF_LIGHT) -> float:
    """Relativistic Doppler redshift for receding velocity ``v`` (m/s)."""
    if velocity_ms < 0.0:
        raise ValueError(f"velocity must be non-negative, got {velocity_ms!r}")
    beta = velocity_ms / c
    if beta >= 1.0:
        raise ValueError(f"velocity must be below c, got {velocity_ms!r}")
    return math.sqrt((1.0 + beta) / (1.0 - beta)) - 1.0


def density_scaling(component: str, redshift: float) -> float:
    """Density relative to today: matter ``(1+z)^3``, radiation ``(1+z)^4``."""
    if redshift < 0.0:
        raise ValueError(f"redshift must be non-negative, got {redshift!r}")
    if component == "matter":
        return (1.0 + redshift) ** 3
    if component == "radiation":
        return (1.0 + redshift) ** 4
    if component == "lambda":
        return 1.0
    raise ValueError(f"unknown component: {component!r}")


def luminosity_distance_linear_mpc(
    redshift: float, h0: float = HUBBLE_CONSTANT_DEFAULT
) -> float:
    """Linear Hubble-law luminosity distance (Mpc).

    Low-redshift approximation only (``z << 1``); full integration is
    out of scope for the foundation.
    """
    if redshift < 0.0:
        raise ValueError(f"redshift must be non-negative, got {redshift!r}")
    meters_per_mpc = KM_PER_MPC * 1000.0
    return (SPEED_OF_LIGHT * redshift / _h0_per_second(h0)) / meters_per_mpc
