# Physics Foundations

## Overview

Deterministic classical-mechanics primitives in `quantsmind.physics`
(single module `mechanics.py`, SI float quantities, no dependencies).

## Purpose

Let users experiment with projectile motion, Newtonian dynamics,
mechanical energy, and basic wave relations without any setup.

## Concept

Closed-form laws over validated inputs: speeds, masses, and angles are
checked (finite, non-negative, angles within [0, 90]); violations raise
`ValueError`.

## API

`projectile_range`, `projectile_max_height`, `flight_time`,
`kinetic_energy`, `potential_energy`, `momentum`, `newton_second_law`,
`wave_speed`, `wave_energy`, `mass_energy`, `heat_conduction`, plus exact
constants `STANDARD_GRAVITY`, `SPEED_OF_LIGHT`, `PLANCK_CONSTANT`.

## Input / Processing / Output

Input: speeds (m/s), angles (degrees), masses (kg), frequencies (Hz).
Processing: closed-form evaluation. Output: SI floats (m, s, J, N, m/s).

## Example

`python examples/physics/projectile.py` prints range/height/time across
launch angles and proves the 45-degree optimum on flat ground.

## Limitations

Point-mass flat-ground ballistics only; no drag, no relativity (except
`mass_energy`), no rigid-body or fluid dynamics. Constants are exact
defined values, not the registry-backed scientific constants.
