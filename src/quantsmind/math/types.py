"""
Mathematics Package Type Definitions

This module defines all type aliases and type hints used throughout the Mathematics package.
Type definitions provide type safety and improve code documentation.

Purpose
-------
Provide centralized type definitions for the Mathematics package.

Scientific Meaning
------------------
Types represent the fundamental data structures used in mathematical computing,
ensuring type safety and enabling static analysis.

Responsibilities
----------------
- Define type aliases
- Provide type hints
- Enable static type checking
- Improve code documentation
- Support IDE autocomplete

Dependencies
------------
typing (standard library)

Future Extensions
-----------------
- Generic type constraints
- Protocol definitions
- Type guards
"""

from __future__ import annotations

from typing import Any, Callable, List, Tuple, Union

# Scalar types
Scalar = Union[int, float, complex]
Real = Union[int, float]
Integer = int
Float = float
Complex = complex

# Vector types
Vector = List[Scalar]
RealVector = List[Real]
ComplexVector = List[Complex]

# Matrix types
Matrix = List[List[Scalar]]
RealMatrix = List[List[Real]]
ComplexMatrix = List[List[Complex]]

# Tensor types
Tensor = List[Any]
TensorShape = Tuple[int, ...]

# Shape types
Shape = Tuple[int, ...]
Dimension = int
Dimensions = Tuple[int, ...]

# Index types
Index = int
Indices = Tuple[int, ...]
Slice = slice

# Function types
ScalarFunction = Callable[[Scalar], Scalar]
VectorFunction = Callable[[Vector], Vector]
MatrixFunction = Callable[[Matrix], Matrix]

# Probability types
Probability = float
ProbabilityDistribution = Callable[[Scalar], float]

# Optimization types
ObjectiveFunction = Callable[[Vector], Scalar]
ConstraintFunction = Callable[[Vector], bool]

# Graph types
Node = Any
Edge = Tuple[Node, Node]
AdjacencyMatrix = Matrix

# Geometry types
Point = Tuple[float, ...]
Line = Tuple[Point, Point]
Plane = Tuple[Point, Point, Point]

# Numerical types
Tolerance = float
IterationLimit = int
ConvergenceCriterion = Callable[[Scalar], bool]

# Result types
ValidationResult = Tuple[bool, List[str]]
SerializationResult = Tuple[bool, str]

# Coordinate types
CartesianCoordinate = Tuple[float, float, float]
PolarCoordinate = Tuple[float, float]
SphericalCoordinate = Tuple[float, float, float]

# Complex number representations
ComplexCartesian = Tuple[float, float]
ComplexPolar = Tuple[float, float]

# Statistical types
Sample = List[Scalar]
Population = List[Scalar]
Statistic = Callable[[Sample], Scalar]

# Transform types
Transform = Callable[[Any], Any]
LinearTransform = Callable[[Vector], Vector]

# Operator types
Operator = Callable[[Any], Any]
BinaryOperator = Callable[[Any, Any], Any]
UnaryOperator = Callable[[Any], Any]

# Export
__all__ = [
    "Scalar",
    "Real",
    "Integer",
    "Float",
    "Complex",
    "Vector",
    "RealVector",
    "ComplexVector",
    "Matrix",
    "RealMatrix",
    "ComplexMatrix",
    "Tensor",
    "TensorShape",
    "Shape",
    "Dimension",
    "Dimensions",
    "Index",
    "Indices",
    "Slice",
    "ScalarFunction",
    "VectorFunction",
    "MatrixFunction",
    "Probability",
    "ProbabilityDistribution",
    "ObjectiveFunction",
    "ConstraintFunction",
    "Node",
    "Edge",
    "AdjacencyMatrix",
    "Point",
    "Line",
    "Plane",
    "Tolerance",
    "IterationLimit",
    "ConvergenceCriterion",
    "ValidationResult",
    "SerializationResult",
    "CartesianCoordinate",
    "PolarCoordinate",
    "SphericalCoordinate",
    "ComplexCartesian",
    "ComplexPolar",
    "Sample",
    "Population",
    "Statistic",
    "Transform",
    "LinearTransform",
    "Operator",
    "BinaryOperator",
    "UnaryOperator",
]
