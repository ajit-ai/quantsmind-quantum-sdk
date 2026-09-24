# Astronomy Foundations

## Overview

Sky calculations in `quantsmind.astronomy` (`sky.py`): angular
separations, AU/light-year/parsec conversions, Keplerian orbits, and
parallax distances from exact defined constants.

## Purpose

Let users derive the year, orbital speeds, and stellar distances from
first principles with plain floats.

## Concept

Haversine for sky angles; `T = 2π√(a³/GM)` for periods; `d = 1/p` for
parallax; conversions off the exact AU.

## API

`angular_separation()`, `au_to_m()`, `m_to_au()`,
`light_year_to_m()`, `parsec_to_m()`, `parallax_distance_pc()`,
`kepler_period()`, `circular_orbital_velocity()`, `distance_modulus()`,
`absolute_magnitude()`, plus exact constants.

## Input / Processing / Output

Input: degrees, meters, kilograms, arcseconds. Processing: closed forms.
Output: degrees, seconds, m/s, parsecs.

## Example

`python examples/astronomy/earth_orbit.py` derives a 365.25-day year and
29.79 km/s orbital speed from 1 AU + 1 solar mass.

## Limitations

Two-body Keplerian model only; no perturbations, no full coordinate
frames, no ephemerides — not an Astropy replacement.
