"""
Visualization Package — Defines rendering-agnostic contracts for visualizing Entities, State,
and simulation trajectories across every domain.

This package is part of the QuantsMind SDK (R0.1.0).
Architecture-only: no implementations, only public interface surface.

Visualization Framework
----------------------
Provides visualization capabilities for mathematical data and results.
"""

from quantsmind.visualization.plotter import Plotter

__all__: list[str] = [
    "Plotter",
]
