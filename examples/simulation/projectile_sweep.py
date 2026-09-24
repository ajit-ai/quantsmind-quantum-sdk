"""Cross-domain chain: math -> physics -> simulation.

Feature: `SimulationEngine` sweeping `projectile_range` over angles.
Purpose: show packages composing — math constants feed physics, the
engine orchestrates the sweep, results stay inspectable.
Input: angles 15..75 step 15, speed 25 m/s.
Processing: one simulation per angle, best range selected.
Output: per-angle ranges plus the 45-degree optimum.
Meaning: composition without coupling; each layer keeps its job.

Run from the repository root::

    python examples/simulation/projectile_sweep.py
"""

from __future__ import annotations

from typing import Any

from quantsmind.physics import projectile_range
from quantsmind.simulation.simulation_engine import SimulationEngine


def _sweep(parameters: dict[str, Any]) -> dict[str, Any]:
    angle = float(parameters["angle"])
    return {"angle": angle, "range": projectile_range(float(parameters["speed"]), angle)}


def main() -> None:
    engine = SimulationEngine()
    engine.register_simulator("sweep", _sweep)
    results = []
    for angle in (15.0, 30.0, 45.0, 60.0, 75.0):
        result = engine.run_simulation("sweep", {"speed": 25.0, "angle": angle})
        assert result.success
        results.append((angle, result.output["range"]))
    for angle, distance in results:
        print(f"angle {angle:.0f}: {distance:.2f} m")
    best = max(results, key=lambda item: item[1])
    print(f"best angle: {best[0]:.0f}")


if __name__ == "__main__":
    main()
