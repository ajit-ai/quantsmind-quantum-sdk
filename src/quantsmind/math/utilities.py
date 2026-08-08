"""
Mathematics Package Utilities Module

This module provides utility functions and helper classes for mathematical operations throughout the Mathematics package.
Utilities provide common mathematical operations and helper functions.

Purpose
-------
Provide utility functions and helper classes for the Mathematics package.

Scientific Meaning
------------------
Utilities provide common mathematical operations: rounding, comparison, conversion,
and helper functions used across mathematical computing applications.

Responsibilities
----------------
- Provide common utility functions
- Support mathematical operations
- Enable type conversions
- Support numerical operations

Dependencies
------------
math (standard library)
typing (standard library)
quantsmind.math.constants (mathematical constants)
quantsmind.math.types (type definitions)

Future Extensions
-----------------
- Performance-optimized utilities
- GPU-accelerated utilities
- Batch operations
- Parallel processing utilities
"""

from __future__ import annotations

import math
from typing import Any, List, Tuple, Union

from quantsmind.math.constants import (
    DEG_TO_RAD,
    FLOAT_EPSILON,
    MACHINE_EPSILON,
    RAD_TO_DEG,
)
from quantsmind.math.types import (
    Complex,
    Float,
    Integer,
    Matrix,
    Real,
    Scalar,
    Shape,
    Vector,
)


def is_close(a: Scalar, b: Scalar, rel_tol: float = 1e-9, abs_tol: float = 0.0) -> bool:
    """Check if two scalars are close within tolerance.

    Args:
        a: First scalar
        b: Second scalar
        rel_tol: Relative tolerance
        abs_tol: Absolute tolerance

    Returns:
        True if values are close, False otherwise

    Example:
        >>> is_close(1.0, 1.000000001)
    """
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def is_zero(value: Scalar, tolerance: float = FLOAT_EPSILON) -> bool:
    """Check if a value is effectively zero.

    Args:
        value: Value to check
        tolerance: Numerical tolerance

    Returns:
        True if value is effectively zero, False otherwise

    Example:
        >>> is_zero(1e-15)
    """
    return abs(value) < tolerance


def is_positive(value: Scalar) -> bool:
    """Check if a value is positive.

    Args:
        value: Value to check

    Returns:
        True if value is positive, False otherwise

    Example:
        >>> is_positive(5.0)
    """
    return value > 0


def is_negative(value: Scalar) -> bool:
    """Check if a value is negative.

    Args:
        value: Value to check

    Returns:
        True if value is negative, False otherwise

    Example:
        >>> is_negative(-5.0)
    """
    return value < 0


def is_integer(value: Scalar, tolerance: float = FLOAT_EPSILON) -> bool:
    """Check if a value is effectively an integer.

    Args:
        value: Value to check
        tolerance: Numerical tolerance

    Returns:
        True if value is effectively an integer, False otherwise

    Example:
        >>> is_integer(5.0)
    """
    return abs(value - round(value)) < tolerance


def clamp(value: Scalar, min_val: Scalar, max_val: Scalar) -> Scalar:
    """Clamp a value to a range.

    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Clamped value

    Example:
        >>> clamp(5.0, 0.0, 10.0)
    """
    return max(min_val, min(max_val, value))


def lerp(a: Scalar, b: Scalar, t: Scalar) -> Scalar:
    """Linear interpolation between two values.

    Args:
        a: First value
        b: Second value
        t: Interpolation parameter (0 to 1)

    Returns:
        Interpolated value

    Example:
        >>> lerp(0.0, 10.0, 0.5)
    """
    return a + (b - a) * t


def deg_to_rad(degrees: Float) -> Float:
    """Convert degrees to radians.

    Args:
        degrees: Angle in degrees

    Returns:
        Angle in radians

    Example:
        >>> deg_to_rad(180.0)
    """
    return degrees * DEG_TO_RAD


def rad_to_deg(radians: Float) -> Float:
    """Convert radians to degrees.

    Args:
        radians: Angle in radians

    Returns:
        Angle in degrees

    Example:
        >>> rad_to_deg(math.pi)
    """
    return radians * RAD_TO_DEG


def normalize_angle(radians: Float) -> Float:
    """Normalize an angle to [0, 2π).

    Args:
        radians: Angle in radians

    Returns:
        Normalized angle

    Example:
        >>> normalize_angle(7.0)
    """
    return radians % (2 * math.pi)


def magnitude(vector: Vector) -> Float:
    """Calculate the magnitude (Euclidean norm) of a vector.

    Args:
        vector: Vector to calculate magnitude

    Returns:
        Vector magnitude

    Example:
        >>> magnitude([3.0, 4.0])
    """
    return math.sqrt(sum(x * x for x in vector))


def normalize(vector: Vector) -> Vector:
    """Normalize a vector to unit length.

    Args:
        vector: Vector to normalize

    Returns:
        Normalized vector

    Raises:
        ZeroDivisionError: If vector has zero magnitude

    Example:
        >>> normalize([3.0, 4.0])
    """
    mag = magnitude(vector)
    if mag == 0:
        raise ZeroDivisionError("Cannot normalize zero vector")
    return [x / mag for x in vector]


def dot_product(v1: Vector, v2: Vector) -> Float:
    """Calculate the dot product of two vectors.

    Args:
        v1: First vector
        v2: Second vector

    Returns:
        Dot product

    Raises:
        ValueError: If vectors have different lengths

    Example:
        >>> dot_product([1.0, 2.0], [3.0, 4.0])
    """
    if len(v1) != len(v2):
        raise ValueError(f"Vector lengths differ: {len(v1)} vs {len(v2)}")
    return sum(a * b for a, b in zip(v1, v2))


def cross_product_2d(v1: Vector, v2: Vector) -> Float:
    """Calculate the 2D cross product (scalar) of two vectors.

    Args:
        v1: First vector (2D)
        v2: Second vector (2D)

    Returns:
        Cross product scalar

    Example:
        >>> cross_product_2d([1.0, 0.0], [0.0, 1.0])
    """
    return v1[0] * v2[1] - v1[1] * v2[0]


def cross_product_3d(v1: Vector, v2: Vector) -> Vector:
    """Calculate the 3D cross product of two vectors.

    Args:
        v1: First vector (3D)
        v2: Second vector (3D)

    Returns:
        Cross product vector

    Example:
        >>> cross_product_3d([1.0, 0.0, 0.0], [0.0, 1.0, 0.0])
    """
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0],
    ]


def distance(v1: Vector, v2: Vector) -> Float:
    """Calculate the Euclidean distance between two vectors.

    Args:
        v1: First vector
        v2: Second vector

    Returns:
        Euclidean distance

    Raises:
        ValueError: If vectors have different lengths

    Example:
        >>> distance([0.0, 0.0], [3.0, 4.0])
    """
    if len(v1) != len(v2):
        raise ValueError(f"Vector lengths differ: {len(v1)} vs {len(v2)}")
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))


def angle_between(v1: Vector, v2: Vector) -> Float:
    """Calculate the angle between two vectors in radians.

    Args:
        v1: First vector
        v2: Second vector

    Returns:
        Angle in radians

    Raises:
        ValueError: If vectors have different lengths or have zero magnitude

    Example:
        >>> angle_between([1.0, 0.0], [0.0, 1.0])
    """
    if len(v1) != len(v2):
        raise ValueError(f"Vector lengths differ: {len(v1)} vs {len(v2)}")

    mag1 = magnitude(v1)
    mag2 = magnitude(v2)

    if mag1 == 0 or mag2 == 0:
        raise ValueError("Cannot calculate angle with zero-magnitude vector")

    dot = dot_product(v1, v2)
    cos_angle = dot / (mag1 * mag2)
    # Clamp to [-1, 1] to avoid numerical issues
    cos_angle = max(-1.0, min(1.0, cos_angle))
    return math.acos(cos_angle)


def project(v: Vector, onto: Vector) -> Vector:
    """Project one vector onto another.

    Args:
        v: Vector to project
        onto: Vector to project onto

    Returns:
        Projected vector

    Raises:
        ValueError: If vectors have different lengths or onto has zero magnitude

    Example:
        >>> project([1.0, 2.0], [1.0, 0.0])
    """
    if len(v) != len(onto):
        raise ValueError(f"Vector lengths differ: {len(v)} vs {len(onto)}")

    mag_onto = magnitude(onto)
    if mag_onto == 0:
        raise ValueError("Cannot project onto zero vector")

    dot = dot_product(v, onto)
    scale = dot / (mag_onto ** 2)
    return [scale * x for x in onto]


def get_shape(matrix: Matrix) -> Shape:
    """Get the shape of a matrix.

    Args:
        matrix: Matrix to get shape

    Returns:
        Shape tuple (rows, cols)

    Example:
        >>> get_shape([[1, 2], [3, 4]])
    """
    if not matrix:
        return (0, 0)
    return (len(matrix), len(matrix[0]))


def transpose(matrix: Matrix) -> Matrix:
    """Transpose a matrix.

    Args:
        matrix: Matrix to transpose

    Returns:
        Transposed matrix

    Example:
        >>> transpose([[1, 2], [3, 4]])
    """
    return [list(row) for row in zip(*matrix)]


def is_square(matrix: Matrix) -> bool:
    """Check if a matrix is square.

    Args:
        matrix: Matrix to check

    Returns:
        True if square, False otherwise

    Example:
        >>> is_square([[1, 2], [3, 4]])
    """
    if not matrix:
        return False
    shape = get_shape(matrix)
    return shape[0] == shape[1]


def trace(matrix: Matrix) -> Float:
    """Calculate the trace of a square matrix.

    Args:
        matrix: Square matrix

    Returns:
        Trace (sum of diagonal elements)

    Raises:
        ValueError: If matrix is not square

    Example:
        >>> trace([[1, 2], [3, 4]])
    """
    if not is_square(matrix):
        raise ValueError("Matrix must be square")

    return sum(matrix[i][i] for i in range(len(matrix)))


def round_scalar(value: Scalar, precision: int = 6) -> Scalar:
    """Round a scalar to specified precision.

    Args:
        value: Value to round
        precision: Number of decimal places

    Returns:
        Rounded value

    Example:
        >>> round_scalar(3.14159265359, 2)
    """
    return round(value, precision)


def round_vector(vector: Vector, precision: int = 6) -> Vector:
    """Round all elements of a vector.

    Args:
        vector: Vector to round
        precision: Number of decimal places

    Returns:
        Rounded vector

    Example:
        >>> round_vector([3.14159, 2.71828], 2)
    """
    return [round_scalar(x, precision) for x in vector]


def round_matrix(matrix: Matrix, precision: int = 6) -> Matrix:
    """Round all elements of a matrix.

    Args:
        matrix: Matrix to round
        precision: Number of decimal places

    Returns:
        Rounded matrix

    Example:
        >>> round_matrix([[3.14159, 2.71828], [1.41421, 1.73205]], 2)
    """
    return [round_vector(row, precision) for row in matrix]


# Export
__all__ = [
    "is_close",
    "is_zero",
    "is_positive",
    "is_negative",
    "is_integer",
    "clamp",
    "lerp",
    "deg_to_rad",
    "rad_to_deg",
    "normalize_angle",
    "magnitude",
    "normalize",
    "dot_product",
    "cross_product_2d",
    "cross_product_3d",
    "distance",
    "angle_between",
    "project",
    "get_shape",
    "transpose",
    "is_square",
    "trace",
    "round_scalar",
    "round_vector",
    "round_matrix",
]
