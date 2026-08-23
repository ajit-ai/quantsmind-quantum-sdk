"""
Mathematics Package Validation Module

This module provides validation utilities for mathematical operations throughout the Mathematics package.
Validation ensures data integrity and correctness in mathematical computing applications.

Purpose
-------
Provide validation utilities for the Mathematics package.

Scientific Meaning
------------------
Validation ensures mathematical correctness and data integrity in scientific computing,
preventing invalid operations and ensuring consistent behavior.

Responsibilities
----------------
- Provide common validation functions
- Support dimension validation
- Enable range validation
- Support custom validators

Dependencies
------------
typing (standard library)
quantsmind.math.exceptions (exception hierarchy)
quantsmind.math.types (type definitions)

Future Extensions
-----------------
- Async validators
- Composite validators
- Validator composition
- Validator caching
"""

from __future__ import annotations

import logging
from typing import Any

from quantsmind.math.types import (
    Matrix,
    Scalar,
    Shape,
    Vector,
)

logger = logging.getLogger(__name__)


def validate_scalar(value: Any) -> tuple[bool, list[str]]:
    """Validate that a value is a scalar.

    Args:
        value: Value to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_scalar(42.0)
    """
    if isinstance(value, (int, float, complex)):
        return (True, [])
    return (False, [f"Expected scalar, got {type(value).__name__}"])


def validate_vector(vector: Vector) -> tuple[bool, list[str]]:
    """Validate that a value is a valid vector.

    Args:
        vector: Vector to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_vector([1.0, 2.0, 3.0])
    """
    if not isinstance(vector, (list, tuple)):
        return (False, [f"Vector must be list or tuple, got {type(vector).__name__}"])

    if len(vector) == 0:
        return (False, ["Vector cannot be empty"])

    for i, element in enumerate(vector):
        if not isinstance(element, (int, float, complex)):
            return (False, [f"Element {i} is not a scalar: {type(element).__name__}"])

    return (True, [])


def validate_matrix(matrix: Matrix) -> tuple[bool, list[str]]:
    """Validate that a value is a valid matrix.

    Args:
        matrix: Matrix to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_matrix([[1.0, 2.0], [3.0, 4.0]])
    """
    if not isinstance(matrix, (list, tuple)):
        return (False, [f"Matrix must be list or tuple, got {type(matrix).__name__}"])

    if len(matrix) == 0:
        return (False, ["Matrix cannot be empty"])

    row_length = None
    for i, row in enumerate(matrix):
        if not isinstance(row, (list, tuple)):
            return (False, [f"Row {i} is not a list or tuple: {type(row).__name__}"])

        if len(row) == 0:
            return (False, [f"Row {i} cannot be empty"])

        if row_length is None:
            row_length = len(row)
        elif len(row) != row_length:
            return (False, [f"Row {i} has inconsistent length: {len(row)} vs {row_length}"])

        for j, element in enumerate(row):
            if not isinstance(element, (int, float, complex)):
                return (False, [f"Element ({i},{j}) is not a scalar: {type(element).__name__}"])

    return (True, [])


def validate_shape(shape: Shape, expected: Shape) -> tuple[bool, list[str]]:
    """Validate that a shape matches the expected shape.

    Args:
        shape: Actual shape
        expected: Expected shape

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_shape((2, 3), (2, 3))
    """
    if shape != expected:
        return (False, [f"Shape mismatch: {shape} vs {expected}"])
    return (True, [])


def validate_dimensions_compatible(shape1: Shape, shape2: Shape) -> tuple[bool, list[str]]:
    """Validate that two shapes are compatible for operations.

    Args:
        shape1: First shape
        shape2: Second shape

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_dimensions_compatible((2, 3), (3, 4))
    """
    if len(shape1) == 0 or len(shape2) == 0:
        return (False, ["Shapes cannot be empty"])

    if shape1[-1] != shape2[0]:
        return (False, [f"Dimensions incompatible: {shape1} vs {shape2}"])

    return (True, [])


def validate_probability(value: float) -> tuple[bool, list[str]]:
    """Validate that a value is a valid probability.

    Args:
        value: Probability value to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_probability(0.5)
    """
    if not isinstance(value, (int, float)):
        return (False, [f"Probability must be numeric, got {type(value).__name__}"])

    if value < 0 or value > 1:
        return (False, [f"Probability must be in [0, 1], got {value}"])

    return (True, [])


def validate_non_zero(value: Scalar, tolerance: float = 1e-10) -> tuple[bool, list[str]]:
    """Validate that a value is non-zero within tolerance.

    Args:
        value: Value to validate
        tolerance: Numerical tolerance

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_non_zero(5.0)
    """
    if abs(value) < tolerance:
        return (False, [f"Value is effectively zero: {value}"])
    return (True, [])


def validate_positive(value: Scalar) -> tuple[bool, list[str]]:
    """Validate that a value is positive.

    Args:
        value: Value to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_positive(5.0)
    """
    if not isinstance(value, (int, float)):
        return (False, [f"Value must be numeric, got {type(value).__name__}"])

    if value <= 0:
        return (False, [f"Value must be positive, got {value}"])

    return (True, [])


def validate_non_negative(value: Scalar) -> tuple[bool, list[str]]:
    """Validate that a value is non-negative.

    Args:
        value: Value to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_non_negative(5.0)
    """
    if not isinstance(value, (int, float)):
        return (False, [f"Value must be numeric, got {type(value).__name__}"])

    if value < 0:
        return (False, [f"Value must be non-negative, got {value}"])

    return (True, [])


def validate_square_matrix(matrix: Matrix) -> tuple[bool, list[str]]:
    """Validate that a matrix is square.

    Args:
        matrix: Matrix to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_square_matrix([[1.0, 2.0], [3.0, 4.0]])
    """
    is_valid, errors = validate_matrix(matrix)
    if not is_valid:
        return (is_valid, errors)

    rows = len(matrix)
    cols = len(matrix[0]) if matrix else 0

    if rows != cols:
        return (False, [f"Matrix is not square: {rows}x{cols}"])

    return (True, [])


def validate_symmetric_matrix(matrix: Matrix, tolerance: float = 1e-10) -> tuple[bool, list[str]]:
    """Validate that a matrix is symmetric.

    Args:
        matrix: Matrix to validate
        tolerance: Numerical tolerance for comparison

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_symmetric_matrix([[1.0, 2.0], [2.0, 1.0]])
    """
    is_valid, errors = validate_square_matrix(matrix)
    if not is_valid:
        return (is_valid, errors)

    n = len(matrix)
    for i in range(n):
        for j in range(i + 1, n):
            if abs(matrix[i][j] - matrix[j][i]) > tolerance:
                return (False, [f"Matrix is not symmetric: element ({i},{j}) != ({j},{i})"])

    return (True, [])


def validate_orthogonal_matrix(matrix: Matrix, tolerance: float = 1e-10) -> tuple[bool, list[str]]:
    """Validate that a matrix is orthogonal.

    Args:
        matrix: Matrix to validate
        tolerance: Numerical tolerance for comparison

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_orthogonal_matrix([[1.0, 0.0], [0.0, 1.0]])
    """
    is_valid, errors = validate_square_matrix(matrix)
    if not is_valid:
        return (is_valid, errors)

    # Check that M^T * M = I
    n = len(matrix)
    for i in range(n):
        for j in range(n):
            dot_product = sum(matrix[k][i] * matrix[k][j] for k in range(n))
            expected = 1.0 if i == j else 0.0
            if abs(dot_product - expected) > tolerance:
                return (False, [f"Matrix is not orthogonal: ({i},{j}) dot product = {dot_product}"])

    return (True, [])


class Validator:
    """Base class for custom validators.

    This class provides a framework for creating reusable validators
    with pre-conditions and post-conditions.

    Example:
        >>> class PositiveValidator(Validator):
        ...     def validate(self, value: Any) -> Tuple[bool, List[str]]:
        ...         return validate_positive(value)
    """

    def validate(self, value: Any) -> tuple[bool, list[str]]:
        """Validate a value.

        Args:
            value: Value to validate

        Returns:
            Tuple of (is_valid, error_messages)

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement validate method")

    def __call__(self, value: Any) -> tuple[bool, list[str]]:
        """Make the validator callable.

        Args:
            value: Value to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        return self.validate(value)


# Export
__all__ = [
    "validate_scalar",
    "validate_vector",
    "validate_matrix",
    "validate_shape",
    "validate_dimensions_compatible",
    "validate_probability",
    "validate_non_zero",
    "validate_positive",
    "validate_non_negative",
    "validate_square_matrix",
    "validate_symmetric_matrix",
    "validate_orthogonal_matrix",
    "Validator",
]
