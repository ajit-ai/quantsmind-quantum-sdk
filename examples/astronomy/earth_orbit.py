"""Earth's orbit: year length, orbital speed, and a parallax check.

Feature: Keplerian orbits and parallax from ``quantsmind.astronomy``.
Purpose: derive the year from AU + solar mass, no lookup tables.
Input: 1 AU orbit around 1 solar mass; 0.5 arcsec parallax.
Processing: Kepler period, circular velocity, distance flip.
Output: ~365.2-day year, ~29.8 km/s, 2.0 pc comparison star.
Meaning: Newton's law plus exact constants reproduces the calendar.

Run from the repository root::

    python examples/astronomy/earth_orbit.py
"""

from __future__ import annotations

from quantsmind.astronomy import (
    ASTRONOMICAL_UNIT_M,
    SOLAR_MASS_KG,
    circular_orbital_velocity,
    kepler_period,
    parallax_distance_pc,
)


def main() -> None:
    period_s = kepler_period(ASTRONOMICAL_UNIT_M, SOLAR_MASS_KG)
    print(f"orbital period: {period_s / 86400.0:.2f} days")
    velocity = circular_orbital_velocity(ASTRONOMICAL_UNIT_M, SOLAR_MASS_KG)
    print(f"orbital speed:  {velocity / 1000.0:.2f} km/s")
    print(f"0.5 arcsec parallax -> {parallax_distance_pc(0.5):.1f} pc")


if __name__ == "__main__":
    main()
