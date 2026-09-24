"""Hubble flow: recession, scale factor, and cosmic scales.

Feature: expansion relations from ``quantsmind.cosmology``.
Purpose: connect redshift, scale factor, and the Hubble scales.
Input: z = 0.1 galaxy, H0 = 70 km/s/Mpc.
Processing: velocity, scale factor, Hubble distance/time, densities.
Output: 7000 km/s recession at a = 0.909, 13.97 Gyr Hubble time.
Meaning: linear relations describe the nearby universe (z << 1).

Run from the repository root::

    python examples/cosmology/hubble_flow.py
"""

from __future__ import annotations

from quantsmind.cosmology import (
    density_scaling,
    hubble_distance_mpc,
    hubble_time_gyr,
    hubble_velocity,
    luminosity_distance_linear_mpc,
    scale_factor,
)


def main() -> None:
    redshift = 0.1
    print(f"recession at 100 Mpc: {hubble_velocity(100.0):.0f} km/s")
    print(f"scale factor at z=0.1: {scale_factor(redshift):.3f}")
    print(f"luminosity distance: {luminosity_distance_linear_mpc(redshift):.1f} Mpc")
    print(f"Hubble distance: {hubble_distance_mpc():.1f} Mpc")
    print(f"Hubble time: {hubble_time_gyr():.2f} Gyr")
    print(f"matter density at z=1: {density_scaling('matter', 1.0):.0f}x today")


if __name__ == "__main__":
    main()
