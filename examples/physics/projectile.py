"""Projectile motion: range, height, and flight time vs launch angle.

Feature: classical projectile kinematics over flat ground.
Purpose: show deterministic SI-unit primitives from ``quantsmind.physics``.
Input: launch speed 25 m/s, angles 15/30/45/60/75 degrees.
Processing: closed-form range/height/time per angle.
Output: table proving maximum range at 45 degrees.
Meaning: symmetric rise/fall makes 45 degrees optimal on flat ground.

Run from the repository root::

    python examples/physics/projectile.py
"""

from __future__ import annotations

from quantsmind.physics import flight_time, projectile_max_height, projectile_range

SPEED = 25.0
ANGLES = (15.0, 30.0, 45.0, 60.0, 75.0)


def main() -> None:
    print(f"{'angle':>6} {'range/m':>9} {'height/m':>9} {'time/s':>8}")
    best = (0.0, 0.0)
    for angle in ANGLES:
        distance = projectile_range(SPEED, angle)
        height = projectile_max_height(SPEED, angle)
        duration = flight_time(SPEED, angle)
        print(f"{angle:>6.1f} {distance:>9.2f} {height:>9.2f} {duration:>8.2f}")
        if distance > best[1]:
            best = (angle, distance)
    print(f"optimal angle: {best[0]:.1f} degrees -> {best[1]:.2f} m")


if __name__ == "__main__":
    main()
