"""
Operators Module

This module provides mathematical operators for the Mathematics package.
Operators represent reusable mathematical operations.

Purpose
-------
Provide mathematical operators for the Mathematics package.

Scientific Meaning
------------------
Operators represent mathematical operations that transform inputs to outputs,
essential for algebra, calculus, linear algebra, and many other mathematical domains.

Responsibilities
----------------
- Support basic operators
- Enable operator composition
- Support operator chaining
- Handle operator validation

Dependencies
------------
typing (standard library)
quantsmind.math.exceptions (exception hierarchy)
quantsmind.math.types (type definitions)

Future Extensions
-----------------
- Advanced operators
- Operator optimization
- Operator parallelization
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any, List, Union

from quantsmind.math.exceptions import InvalidOperationError
from quantsmind.math.types import BinaryOperator, Scalar, UnaryOperator

logger = logging.getLogger(__name__)


class AddOperator:
    """Concrete implementation of addition operator.

    This class provides addition operations for scalars and vectors.

    Scientific Meaning
    ------------------
    In mathematics, addition represents the combining of quantities,
    one of the fundamental arithmetic operations.

    Example:
        >>> add = AddOperator()
        >>> result = add.apply(3.0, 5.0)
    """

    def apply(self, a: Scalar, b: Scalar) -> Scalar:
        """Apply addition.

        Args:
            a: First operand
            b: Second operand

        Returns:
            Sum

        Example:
            >>> result = add.apply(3.0, 5.0)
        """
        return a + b

    def __call__(self, a: Scalar, b: Scalar) -> Scalar:
        """Make the operator callable.

        Args:
            a: First operand
            b: Second operand

        Returns:
            Sum

        Example:
            >>> result = add(3.0, 5.0)
        """
        return self.apply(a, b)


class MultiplyOperator:
    """Concrete implementation of multiplication operator.

    This class provides multiplication operations for scalars and vectors.

    Scientific Meaning
    ------------------
    In mathematics, multiplication represents repeated addition,
    one of the fundamental arithmetic operations.

    Example:
        >>> mul = MultiplyOperator()
        >>> result = mul.apply(3.0, 5.0)
    """

    def apply(self, a: Scalar, b: Scalar) -> Scalar:
        """Apply multiplication.

        Args:
            a: First operand
            b: Second operand

        Returns:
            Product

        Example:
            >>> result = mul.apply(3.0, 5.0)
        """
        return a * b

    def __call__(self, a: Scalar, b: Scalar) -> Scalar:
        """Make the operator callable.

        Args:
            a: First operand
            b: Second operand

        Returns:
            Product

        Example:
            >>> result = mul(3.0, 5.0)
        """
        return self.apply(a, b)


class SubtractOperator:
    """Concrete implementation of subtraction operator.

    This class provides subtraction operations for scalars and vectors.

    Scientific Meaning
    ------------------
    In mathematics, subtraction represents the difference between quantities,
    one of the fundamental arithmetic operations.

    Example:
        >>> sub = SubtractOperator()
        >>> result = sub.apply(5.0, 3.0)
    """

    def apply(self, a: Scalar, b: Scalar) -> Scalar:
        """Apply subtraction.

        Args:
            a: First operand
            b: Second operand

        Returns:
            Difference

        Example:
            >>> result = sub.apply(5.0, 3.0)
        """
        return a - b

    def __call__(self, a: Scalar, b: Scalar) -> Scalar:
        """Make the operator callable.

        Args:
            a: First operand
            b: Second operand

        Returns:
            Difference

        Example:
            >>> result = sub(5.0, 3.0)
        """
        return self.apply(a, b)


class DivideOperator:
    """Concrete implementation of division operator.

    This class provides division operations for scalars.

    Scientific Meaning
    ------------------
    In mathematics, division represents the ratio between quantities,
    one of the fundamental arithmetic operations.

    Example:
        >>> div = DivideOperator()
        >>> result = div.apply(10.0, 2.0)
    """

    def apply(self, a: Scalar, b: Scalar) -> Scalar:
        """Apply division.

        Args:
            a: Numerator
            b: Denominator

        Returns:
            Quotient

        Raises:
            InvalidOperationError: If dividing by zero

        Example:
            >>> result = div.apply(10.0, 2.0)
        """
        if b == 0:
            raise InvalidOperationError("Cannot divide by zero")
        return a / b

    def __call__(self, a: Scalar, b: Scalar) -> Scalar:
        """Make the operator callable.

        Args:
            a: Numerator
            b: Denominator

        Returns:
            Quotient

        Example:
            >>> result = div(10.0, 2.0)
        """
        return self.apply(a, b)


class PowerOperator:
    """Concrete implementation of power operator.

    This class provides exponentiation operations.

    Scientific Meaning
    ------------------
    In mathematics, exponentiation represents repeated multiplication,
    essential for many mathematical operations.

    Example:
        >>> power = PowerOperator()
        >>> result = power.apply(2.0, 3.0)
    """

    def apply(self, a: Scalar, b: Scalar) -> Scalar:
        """Apply exponentiation.

        Args:
            a: Base
            b: Exponent

        Returns:
            Power

        Example:
            >>> result = power.apply(2.0, 3.0)
        """
        return a ** b

    def __call__(self, a: Scalar, b: Scalar) -> Scalar:
        """Make the operator callable.

        Args:
            a: Base
            b: Exponent

        Returns:
            Power

        Example:
            >>> result = power(2.0, 3.0)
        """
        return self.apply(a, b)


class MatrixOperator:
    """Concrete implementation of matrix operator.

    This class provides matrix operations.

    Scientific Meaning
    ------------------
    In linear algebra, matrix operators represent linear transformations,
    essential for many scientific computing applications.

    Example:
        >>> mat_op = MatrixOperator()
        >>> result = mat_op.apply(matrix, vector)
    """

    def apply(self, matrix: Any, vector: Any) -> Any:
        """Apply matrix operation.

        Args:
            matrix: Matrix
            vector: Vector

        Returns:
            Result

        Raises:
            NotImplementedError: If not implemented

        Example:
            >>> result = mat_op.apply(matrix, vector)
        """
        raise NotImplementedError("Matrix operator not yet implemented")


class TensorOperator:
    """Concrete implementation of tensor operator.

    This class provides tensor operations.

    Scientific Meaning
    ------------------
    In tensor calculus, tensor operators represent operations on multi-dimensional arrays,
    essential for quantum mechanics and general relativity.

    Example:
        >>> tensor_op = TensorOperator()
        >>> result = tensor_op.apply(tensor1, tensor2)
    """

    def apply(self, tensor1: Any, tensor2: Any) -> Any:
        """Apply tensor operation.

        Args:
            tensor1: First tensor
            tensor2: Second tensor

        Returns:
            Result

        Raises:
            NotImplementedError: If not implemented

        Example:
            >>> result = tensor_op.apply(tensor1, tensor2)
        """
        raise NotImplementedError("Tensor operator not yet implemented")


class ComposedOperator:
    """Concrete implementation of composed operator.

    This class represents the composition of multiple operators.

    Scientific Meaning
    ------------------
    In mathematics, operator composition represents applying one operator after another,
    essential for building complex operations from simple ones.

    Example:
        >>> composed = ComposedOperator([AddOperator(), MultiplyOperator()])
    """

    def __init__(self, operators: list[Any]) -> None:
        """Initialize a ComposedOperator.

        Args:
            operators: List of operators to compose

        Example:
            >>> composed = ComposedOperator([AddOperator(), MultiplyOperator()])
        """
        self._operators = operators
        logger.debug(f"Created composed operator with {len(operators)} operators")

    def apply(self, *args: Any) -> Any:
        """Apply composed operators.

        Args:
            args: Arguments to apply

        Returns:
            Result

        Example:
            >>> result = composed.apply(3.0, 5.0)
        """
        result = args
        for operator in self._operators:
            result = operator.apply(result[0]) if len(result) == 1 else operator.apply(*result)
        return result

    def __call__(self, *args: Any) -> Any:
        """Make the operator callable.

        Args:
            args: Arguments to apply

        Returns:
            Result

        Example:
            >>> result = composed(3.0, 5.0)
        """
        return self.apply(*args)


# Export
__all__ = [
    "AddOperator",
    "MultiplyOperator",
    "SubtractOperator",
    "DivideOperator",
    "PowerOperator",
    "MatrixOperator",
    "TensorOperator",
    "ComposedOperator",
]
