"""
Simulation Package — Defines generic contracts for simulating the evolution of Systems over
Space and Time, independent of physical domain.

This package is part of the QuantsMind SDK (R0.1.0).
Architecture-only: no implementations, only public interface surface.

Simulation Framework
-------------------
Provides comprehensive simulation capabilities for mathematical and scientific modeling.
"""

from quantsmind.simulation.simulation_engine import (
    Experiment,
    SimulationEngine,
    SimulationResult,
    Simulator,
)

__all__: list[str] = [
    "SimulationEngine",
    "Simulator",
    "SimulationResult",
    "Experiment",
]
