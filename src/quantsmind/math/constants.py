"""
Mathematical Constants Module

This module provides fundamental mathematical constants used throughout the Mathematics package.
Constants provide high-precision values for mathematical operations.

Purpose
-------
Provide fundamental mathematical constants for the Mathematics package.

Scientific Meaning
------------------
Constants represent fundamental mathematical values: π, e, τ, φ, √2, machine epsilon,
and other important mathematical constants used in scientific computing.

Responsibilities
----------------
- Provide high-precision constants
- Support different precision levels
- Enable constant access
- Provide constant documentation

Dependencies
------------
math (standard library)
typing (standard library)

Future Extensions
-----------------
- Physical constants
- Conversion factors
- Domain-specific constants
"""

from __future__ import annotations

import math
from typing import Final

# Fundamental constants
PI: Final[float] = math.pi  # π ≈ 3.141592653589793
E: Final[float] = math.e  # e ≈ 2.718281828459045
TAU: Final[float] = 2 * math.pi  # τ = 2π ≈ 6.283185307179586
PHI: Final[float] = (1 + math.sqrt(5)) / 2  # φ ≈ 1.618033988749895
SQRT2: Final[float] = math.sqrt(2)  # √2 ≈ 1.4142135623730951
SQRT3: Final[float] = math.sqrt(3)  # √3 ≈ 1.7320508075688772
LN2: Final[float] = math.log(2)  # ln(2) ≈ 0.6931471805599453
LN10: Final[float] = math.log(10)  # ln(10) ≈ 2.302585092994046
LOG2E: Final[float] = math.log2(math.e)  # log₂(e) ≈ 1.4426950408889634
LOG10E: Final[float] = math.log10(math.e)  # log₁₀(e) ≈ 0.4342944819032518

# Numerical precision constants
MACHINE_EPSILON: Final[float] = math.ulp(1.0)  # Machine epsilon ≈ 2.220446049250313e-16
FLOAT_EPSILON: Final[float] = 1e-10  # Float precision tolerance
DOUBLE_EPSILON: Final[float] = 1e-15  # Double precision tolerance

# Angle constants
DEG_TO_RAD: Final[float] = math.pi / 180  # Degrees to radians conversion
RAD_TO_DEG: Final[float] = 180 / math.pi  # Radians to degrees conversion

# Infinity and NaN
POSITIVE_INFINITY: Final[float] = float('inf')
NEGATIVE_INFINITY: Final[float] = float('-inf')
NAN: Final[float] = float('nan')

# Physical constants (approximate values)
SPEED_OF_LIGHT: Final[float] = 299792458.0  # c ≈ 299,792,458 m/s
PLANCK_CONSTANT: Final[float] = 6.62607015e-34  # h ≈ 6.62607015×10⁻³⁴ J·s
BOLTZMANN_CONSTANT: Final[float] = 1.380649e-23  # k ≈ 1.380649×10⁻²³ J/K
AVOGADRO_NUMBER: Final[float] = 6.02214076e23  # Nₐ ≈ 6.02214076×10²³ mol⁻¹
GRAVITATIONAL_CONSTANT: Final[float] = 6.67430e-11  # G ≈ 6.67430×10⁻¹¹ m³·kg⁻¹·s⁻²

# Mathematical constants
EULER_MASCHERONI: Final[float] = 0.5772156649015329  # γ ≈ 0.5772156649015329
CATALAN_CONSTANT: Final[float] = 0.915965594177219  # G ≈ 0.915965594177219
APERY_CONSTANT: Final[float] = 1.202056903159594  # ζ(3) ≈ 1.202056903159594


class Constants:
    """Class for accessing mathematical constants.

    This class provides a convenient interface for accessing mathematical
    constants with optional precision control.

    Example:
        >>> constants = Constants()
        >>> print(constants.pi)
        3.141592653589793
    """

    def __init__(self, precision: int = 15) -> None:
        """Initialize Constants with specified precision.

        Args:
            precision: Number of decimal places for constants
        """
        self._precision = precision

    @property
    def pi(self) -> float:
        """Get π (pi)."""
        return round(PI, self._precision)

    @property
    def e(self) -> float:
        """Get e (Euler's number)."""
        return round(E, self._precision)

    @property
    def tau(self) -> float:
        """Get τ (tau = 2π)."""
        return round(TAU, self._precision)

    @property
    def phi(self) -> float:
        """Get φ (golden ratio)."""
        return round(PHI, self._precision)

    @property
    def sqrt2(self) -> float:
        """Get √2."""
        return round(SQRT2, self._precision)

    @property
    def machine_epsilon(self) -> float:
        """Get machine epsilon."""
        return MACHINE_EPSILON

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Constants(precision={self._precision})"


# Default constants instance
DEFAULT_CONSTANTS = Constants()


# Export
__all__ = [
    "PI",
    "E",
    "TAU",
    "PHI",
    "SQRT2",
    "SQRT3",
    "LN2",
    "LN10",
    "LOG2E",
    "LOG10E",
    "MACHINE_EPSILON",
    "FLOAT_EPSILON",
    "DOUBLE_EPSILON",
    "DEG_TO_RAD",
    "RAD_TO_DEG",
    "POSITIVE_INFINITY",
    "NEGATIVE_INFINITY",
    "NAN",
    "SPEED_OF_LIGHT",
    "PLANCK_CONSTANT",
    "BOLTZMANN_CONSTANT",
    "AVOGADRO_NUMBER",
    "GRAVITATIONAL_CONSTANT",
    "EULER_MASCHERONI",
    "CATALAN_CONSTANT",
    "APERY_CONSTANT",
    "Constants",
    "DEFAULT_CONSTANTS",
]
