"""Foundational astronomy calculations.

Angular separations, astronomical unit conversions, Keplerian orbital
relations, and parallax distances. Angles in degrees, distances in SI
unless noted; constants are exact defined values with sources cited.
Deterministic and dependency-free.
"""

from __future__ import annotations

import math

__all__ = [
    "ASTRONOMICAL_UNIT_M",
    "LIGHT_YEAR_M",
    "PARSEC_M",
    "GRAVITATIONAL_CONSTANT",
    "SOLAR_MASS_KG",
    "angular_separation",
    "au_to_m",
    "m_to_au",
    "light_year_to_m",
    "parsec_to_m",
    "parallax_distance_pc",
    "kepler_period",
    "circular_orbital_velocity",
    "distance_modulus",
    "absolute_magnitude",
]

#: Astronomical unit, exact by IAU 2012 definition (m).
ASTRONOMICAL_UNIT_M = 1.495978707e11
#: Light-year derived from exact Julian year (m).
LIGHT_YEAR_M = 9.4607304725808e15
#: Parsec derived from the exact AU (m).
PARSEC_M = 3.08567758149137e16
#: Newtonian gravitational constant, CODATA 2018 (m^3 kg^-1 s^-2).
GRAVITATIONAL_CONSTANT = 6.67430e-11
#: Solar mass, nominal IAU 2015 value (kg).
SOLAR_MASS_KG = 1.98847e30


def angular_separation(
    ra1_deg: float, dec1_deg: float, ra2_deg: float, dec2_deg: float
) -> float:
    """Angular separation of two sky positions in degrees (haversine)."""
    ra1, dec1 = math.radians(ra1_deg), math.radians(dec1_deg)
    ra2, dec2 = math.radians(ra2_deg), math.radians(dec2_deg)
    haversine = (
        math.sin((dec2 - dec1) / 2.0) ** 2
        + math.cos(dec1) * math.cos(dec2) * math.sin((ra2 - ra1) / 2.0) ** 2
    )
    return math.degrees(2.0 * math.asin(math.sqrt(min(1.0, haversine))))


def au_to_m(au: float) -> float:
    """Astronomical units to meters."""
    if au < 0.0:
        raise ValueError(f"AU must be non-negative, got {au!r}")
    return au * ASTRONOMICAL_UNIT_M


def m_to_au(meters: float) -> float:
    """Meters to astronomical units."""
    if meters < 0.0:
        raise ValueError(f"meters must be non-negative, got {meters!r}")
    return meters / ASTRONOMICAL_UNIT_M


def light_year_to_m(light_years: float) -> float:
    """Light-years to meters."""
    if light_years < 0.0:
        raise ValueError(f"light-years must be non-negative, got {light_years!r}")
    return light_years * LIGHT_YEAR_M


def parsec_to_m(parsecs: float) -> float:
    """Parsecs to meters."""
    if parsecs < 0.0:
        raise ValueError(f"parsecs must be non-negative, got {parsecs!r}")
    return parsecs * PARSEC_M


def parallax_distance_pc(parallax_arcsec: float) -> float:
    """Distance in parsecs from a stellar parallax in arcseconds (d = 1/p)."""
    if parallax_arcsec <= 0.0:
        raise ValueError(f"parallax must be positive, got {parallax_arcsec!r}")
    return 1.0 / parallax_arcsec


def kepler_period(
    semi_major_axis_m: float,
    central_mass_kg: float,
    g_newton: float = GRAVITATIONAL_CONSTANT,
) -> float:
    """Orbital period from Kepler's third law (s)."""
    if semi_major_axis_m <= 0.0:
        raise ValueError(f"semi-major axis must be positive, got {semi_major_axis_m!r}")
    if central_mass_kg <= 0.0:
        raise ValueError(f"central mass must be positive, got {central_mass_kg!r}")
    return 2.0 * math.pi * math.sqrt(semi_major_axis_m**3 / (g_newton * central_mass_kg))


def circular_orbital_velocity(
    radius_m: float,
    central_mass_kg: float,
    g_newton: float = GRAVITATIONAL_CONSTANT,
) -> float:
    """Circular orbital velocity ``sqrt(G*M/r)`` (m/s)."""
    if radius_m <= 0.0:
        raise ValueError(f"radius must be positive, got {radius_m!r}")
    if central_mass_kg <= 0.0:
        raise ValueError(f"central mass must be positive, got {central_mass_kg!r}")
    return math.sqrt(g_newton * central_mass_kg / radius_m)


def distance_modulus(distance_pc: float) -> float:
    """Distance modulus ``m - M = 5*log10(d) - 5`` (magnitudes)."""
    if distance_pc <= 0.0:
        raise ValueError(f"distance must be positive, got {distance_pc!r}")
    return 5.0 * math.log10(distance_pc) - 5.0


def absolute_magnitude(apparent_magnitude: float, distance_pc: float) -> float:
    """Absolute magnitude from apparent magnitude and distance (parsecs)."""
    return float(apparent_magnitude) - distance_modulus(distance_pc)
