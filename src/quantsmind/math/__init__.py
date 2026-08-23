"""
Mathematics Package — Provides the mathematical vocabulary (linear algebra, tensors, geometry,
probability, statistics, calculus, optimization primitives, graph theory, complex numbers,
numerical methods) shared by every scientific domain in the SDK.

This package is part of the QuantsMind SDK (R0.4.0).

Purpose
-------
Provide a comprehensive mathematical foundation for all scientific computing applications
in the QuantsMind SDK, including quantum computing, AI, physics, and finance.

Modules
-------
- exceptions: Mathematical exception hierarchy
- constants: Mathematical and physical constants
- types: Type definitions for mathematical objects
- validation: Validation functions for mathematical objects
- utilities: Utility functions for mathematical operations
- algebra: Abstract algebra structures
- linear_algebra: Vector, matrix, and matrix factory operations
- tensor: Tensor operations
- complex: Complex number operations
- probability: Probability theory and distributions
- statistics: Descriptive and inferential statistics
- geometry: Geometric primitives and transformations
- graph: Graph theory operations
- calculus: Differentiation and integration
- optimization: Optimization algorithms
- numerical: Numerical methods and solvers
- operators: Mathematical operators
- transforms: Mathematical transforms
- topology: Topological structures
- random: Random number generation
"""

from __future__ import annotations

# Foundational modules
# Submodules
from quantsmind.math import (
    algebra,
    calculus,
    complex,
    constants,
    exceptions,
    geometry,
    graph,
    numerical,
    operators,
    optimization,
    probability,
    random,
    statistics,
    tensor,
    topology,
    transforms,
    types,
    utilities,
    validation,
)

# Linear algebra submodule
from quantsmind.math.linear_algebra import factory, matrix, vector

__version__ = "R0.4.0"

__all__ = [
    # Foundational modules
    "constants",
    "exceptions",
    "types",
    "utilities",
    "validation",
    # Submodules
    "algebra",
    "calculus",
    "complex",
    "geometry",
    "graph",
    "numerical",
    "operators",
    "optimization",
    "probability",
    "random",
    "statistics",
    "tensor",
    "topology",
    "transforms",
    # Linear algebra
    "vector",
    "matrix",
    "factory",
    "__version__",
]
