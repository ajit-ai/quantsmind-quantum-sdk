"""
Mathematics Package Exception Hierarchy

This module defines all exception classes used throughout the Mathematics package.
Exceptions provide structured error handling for mathematical operations.

Purpose
-------
Provide structured exception hierarchy for the Mathematics package.

Scientific Meaning
------------------
Exceptions represent mathematical errors: dimension mismatches, singular matrices,
convergence failures, invalid operations, numerical precision issues.

Responsibilities
----------------
- Define base exception class
- Provide specific exception types
- Support error context
- Enable proper error handling

Dependencies
------------
typing (standard library)

Future Extensions
-----------------
- Exception chaining
- Error recovery suggestions
- Detailed error context
"""

from __future__ import annotations


class MathError(Exception):
    """Base exception for all Mathematics package errors.

    This class serves as the root of the exception hierarchy for all
    mathematical operations in the QuantsMind SDK.

    Attributes:
        message: Error message
        context: Optional context dictionary

    Example:
        >>> raise MathError("Mathematical operation failed")
    """

    def __init__(self, message: str, context: dict | None = None) -> None:
        """Initialize a MathError.

        Args:
            message: Error message
            context: Optional context dictionary
        """
        self.message = message
        self.context = context or {}
        super().__init__(self.message)


class DimensionError(MathError):
    """Exception raised when dimensions are incompatible.

    This exception is raised when operations require compatible dimensions
    but the provided dimensions do not match.

    Example:
        >>> raise DimensionError("Matrix dimensions incompatible: (2,3) vs (2,4)")
    """


class SingularMatrixError(MathError):
    """Exception raised when a matrix is singular.

    This exception is raised when operations require a non-singular matrix
    but the provided matrix is singular (determinant is zero).

    Example:
        >>> raise SingularMatrixError("Matrix is singular, cannot compute inverse")
    """


class ConvergenceError(MathError):
    """Exception raised when an iterative method fails to converge.

    This exception is raised when numerical methods fail to converge
    within the specified tolerance or iteration limit.

    Example:
        >>> raise ConvergenceError("Newton-Raphson method failed to converge")
    """


class ValueError(MathError):
    """Exception raised when a value is invalid for a mathematical operation.

    This exception is raised when provided values are outside the valid
    range or do not satisfy required conditions.

    Example:
        >>> raise ValueError("Negative value provided for square root")
    """


class NumericalPrecisionError(MathError):
    """Exception raised when numerical precision is insufficient.

    This exception is raised when operations require higher precision
    than available due to floating-point limitations.

    Example:
        >>> raise NumericalPrecisionError("Loss of significance in subtraction")
    """


class NotImplementedError(MathError):
    """Exception raised when a mathematical operation is not yet implemented.

    This exception is raised for features that are planned but not yet
    implemented in the current version.

    Example:
        >>> raise NotImplementedError("Eigenvalue decomposition not yet implemented")
    """


class DivisionByZeroError(MathError):
    """Exception raised when division by zero is attempted.

    This exception is raised when mathematical operations attempt to divide
    by zero or a value that is effectively zero within numerical tolerance.

    Example:
        >>> raise DivisionByZeroError("Cannot divide by zero")
    """


class InvalidOperationError(MathError):
    """Exception raised when an operation is invalid for the given operands.

    This exception is raised when mathematical operations are attempted on
    operands that do not support the operation.

    Example:
        >>> raise InvalidOperationError("Cannot add matrix and scalar")
    """


class IndexError(MathError):
    """Exception raised when an index is out of bounds.

    This exception is raised when accessing elements outside the valid
    range of vectors, matrices, or tensors.

    Example:
        >>> raise IndexError("Index 5 out of bounds for vector of length 3")
    """


class ShapeError(MathError):
    """Exception raised when tensor shapes are incompatible.

    This exception is raised when tensor operations require compatible
    shapes but the provided shapes do not match.

    Example:
        >>> raise ShapeError("Cannot reshape tensor from (2,3) to (6,)")
    """


class ProbabilityError(MathError):
    """Exception raised when probability values are invalid.

    This exception is raised when probability values are outside the valid
    range [0, 1] or do not sum to 1 as required.

    Example:
        >>> raise ProbabilityError("Probability must be between 0 and 1")
    """


class DistributionError(MathError):
    """Exception raised when distribution parameters are invalid.

    This exception is raised when probability distribution parameters
    are outside their valid ranges.

    Example:
        >>> raise DistributionError("Standard deviation must be positive")
    """


class OptimizationError(MathError):
    """Exception raised when optimization fails.

    This exception is raised when optimization algorithms fail to find
    a solution or encounter numerical issues.

    Example:
        >>> raise OptimizationError("Optimization failed to converge")
    """


class GraphError(MathError):
    """Exception raised for graph-related errors.

    This exception is raised when graph operations encounter issues such
    as missing nodes, invalid edges, or disconnected components.

    Example:
        >>> raise GraphError("Node not found in graph")
    """


class GeometryError(MathError):
    """Exception raised for geometry-related errors.

    This exception is raised when geometric operations encounter issues
    such as invalid coordinates, non-intersecting lines, or degenerate shapes.

    Example:
        >>> raise GeometryError("Points are collinear, cannot form triangle")
    """


# Export
__all__ = [
    "MathError",
    "DimensionError",
    "SingularMatrixError",
    "ConvergenceError",
    "ValueError",
    "NumericalPrecisionError",
    "NotImplementedError",
    "DivisionByZeroError",
    "InvalidOperationError",
    "IndexError",
    "ShapeError",
    "ProbabilityError",
    "DistributionError",
    "OptimizationError",
    "GraphError",
    "GeometryError",
]
