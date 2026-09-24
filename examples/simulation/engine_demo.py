"""Simulation engine: register a doubling model and run it.

Feature: `SimulationEngine` from ``quantsmind.simulation``.
Purpose: show register -> run -> history with no dependencies.
Input: simulator "double" over x = 21.
Processing: engine dispatches to the registered callable.
Output: success result plus one history entry.
Meaning: the engine orchestrates; models stay plain callables.

Run from the repository root::

    python examples/simulation/engine_demo.py
"""

from __future__ import annotations

from quantsmind.simulation.simulation_engine import SimulationEngine


def main() -> None:
    engine = SimulationEngine()
    engine.register_simulator("double", lambda p: {"x": p["x"] * 2})
    result = engine.run_simulation("double", {"x": 21})
    print(f"success: {result.success}")
    print(f"history entries: {len(engine.get_simulation_history())}")


if __name__ == "__main__":
    main()
