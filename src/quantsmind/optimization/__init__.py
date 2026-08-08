"""
Optimization Package — Defines contracts for expressing and solving optimization problems
(objectives, constraints, solvers) used across finance, AI, physics, and quantum domains.

This package is part of the QuantsMind SDK (R0.1.0).
Architecture-only: no implementations, only public interface surface.

Optimization Framework
----------------------
Provides comprehensive optimization algorithms including gradient-based,
evolutionary, and advanced optimization methods.
"""

from quantsmind.optimization.advanced_optimizer import BayesianOptimizer, LBFGSOptimizer, SimulatedAnnealing
from quantsmind.optimization.evolutionary_optimizer import EvolutionaryOptimizer, GeneticAlgorithm, ParticleSwarmOptimizer
from quantsmind.optimization.gradient_optimizer import AdamOptimizer, GradientDescent, GradientOptimizer, NewtonMethod

__all__: list[str] = [
    "GradientOptimizer",
    "GradientDescent",
    "AdamOptimizer",
    "NewtonMethod",
    "EvolutionaryOptimizer",
    "GeneticAlgorithm",
    "ParticleSwarmOptimizer",
    "LBFGSOptimizer",
    "BayesianOptimizer",
    "SimulatedAnnealing",
]
