# Cosmology Foundations

## Overview

Expansion relations in `quantsmind.cosmology` (`expansion.py`): Hubble
velocities, scale-factor/redshift conversion, Hubble distance and time,
relativistic Doppler shift, and component density scalings.

## Purpose

Let users connect redshift, scale factor, and cosmic scales with
transparent low-redshift math.

## Concept

Linear Hubble law plus exact relations (`a = 1/(1+z)`,
matter ∝ (1+z)³, radiation ∝ (1+z)⁴, Λ constant); the luminosity
distance is explicitly a low-z approximation.

## API

`hubble_velocity()`, `scale_factor()`, `redshift_from_scale()`,
`hubble_distance_mpc()`, `hubble_time_gyr()`, `doppler_redshift()`,
`density_scaling()`, `luminosity_distance_linear_mpc()`.

## Input / Processing / Output

Input: Mpc distances, redshifts, H0. Processing: closed forms.
Output: km/s, scale factors, Mpc, Gyr, dimensionless ratios.

## Example

`python examples/cosmology/hubble_flow.py` walks a z = 0.1 galaxy
through velocity, scale, distance, and the 13.97 Gyr Hubble time.

## Limitations

No integrated distances, no perturbation theory, no CMB physics; H0
defaults to 70 km/s/Mpc for examples, not a measurement claim.
