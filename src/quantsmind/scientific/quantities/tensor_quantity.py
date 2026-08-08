"""
Tensor Quantity Module

This module provides tensor quantity definitions for the Scientific package.

Purpose
-------
Provide tensor quantity definitions and operations.

Responsibilities
----------------
- Define tensor quantity structure
- Support tensor arithmetic
- Support tensor operations
- Support tensor validation

Dependencies
------------
typing (standard library)
quantsmind.scientific.quantities.quantity (quantity)
quantsmind.scientific.interfaces (scientific interfaces)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.scientific.interfaces import IDimension, IUnit
from quantsmind.scientific.quantities.quantity import Quantity
from quantsmind.scientific.types import QuantityTensor, QuantityValue


class TensorQuantity(Quantity):
    """Concrete implementation of a tensor quantity.

    This class provides tensor quantity functionality.

    Attributes:
        _value: Tensor values (2D array)
        _unit: Tensor unit
        _dimension: Tensor dimension
        _metadata: Tensor metadata

    Example:
        >>> stress = TensorQuantity([[1.0, 0.0], [0.0, 1.0]], pascal_unit, force_dimension)
        >>> stress.value()
    """

    def __init__(
        self,
        value: QuantityTensor,
        unit: IUnit,
        dimension: IDimension,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a TensorQuantity.

        Args:
            value: Tensor values (2D array)
            unit: Tensor unit
            dimension: Tensor dimension
            metadata: Tensor metadata

        Example:
            >>> stress = TensorQuantity([[1.0, 0.0], [0.0, 1.0]], pascal_unit, force_dimension)
        """
        super().__init__(value, unit, dimension, metadata)

    @property
    def value(self) -> QuantityTensor:
        """Get the tensor values.

        Returns:
            Tensor values

        Example:
            >>> print(f"Value: {tensor.value}")
        """
        return self._value

    @property
    def shape(self) -> tuple[int, int]:
        """Get the tensor shape.

        Returns:
            Tensor shape (rows, columns)

        Example:
            >>> print(f"Shape: {tensor.shape}")
        """
        return (len(self._value), len(self._value[0]) if self._value else 0)

    @property
    def rank(self) -> int:
        """Get the tensor rank.

        Returns:
            Tensor rank (2 for matrix)

        Example:
            >>> print(f"Rank: {tensor.rank}")
        """
        return 2

    def transpose(self) -> "TensorQuantity":
        """Transpose the tensor.

        Returns:
            Transposed tensor

        Example:
            >>> transposed = tensor.transpose()
        """
        transposed_value = [
            [self._value[j][i] for j in range(len(self._value))]
            for i in range(len(self._value[0]) if self._value else 0)
        ]
        return TensorQuantity(transposed_value, self._unit, self._dimension, self._metadata)

    def add(self, other: "TensorQuantity") -> "TensorQuantity":
        """Add tensors.

        Args:
            other: Other tensor

        Returns:
            Resulting tensor

        Raises:
            ValueError: If tensors have different shapes

        Example:
            >>> result = tensor1.add(tensor2)
        """
        if self.shape != other.shape:
            raise ValueError("Tensors must have the same shape")
        
        result_value = [
            [self._value[i][j] + other.value()[i][j] for j in range(len(self._value[0]))]
            for i in range(len(self._value))
        ]
        return TensorQuantity(result_value, self._unit, self._dimension, self._metadata)

    def subtract(self, other: "TensorQuantity") -> "TensorQuantity":
        """Subtract tensors.

        Args:
            other: Other tensor

        Returns:
            Resulting tensor

        Raises:
            ValueError: If tensors have different shapes

        Example:
            >>> result = tensor1.subtract(tensor2)
        """
        if self.shape != other.shape:
            raise ValueError("Tensors must have the same shape")
        
        result_value = [
            [self._value[i][j] - other.value()[i][j] for j in range(len(self._value[0]))]
            for i in range(len(self._value))
        ]
        return TensorQuantity(result_value, self._unit, self._dimension, self._metadata)

    def scale(self, scalar: float) -> "TensorQuantity":
        """Scale the tensor.

        Args:
            scalar: Scale factor

        Returns:
            Scaled tensor

        Example:
            >>> scaled = tensor.scale(2.0)
        """
        result_value = [
            [v * scalar for v in row]
            for row in self._value
        ]
        return TensorQuantity(result_value, self._unit, self._dimension, self._metadata)

    def trace(self) -> float:
        """Calculate the tensor trace.

        Returns:
            Trace (sum of diagonal elements)

        Example:
            >>> trace = tensor.trace()
        """
        return sum(self._value[i][i] for i in range(min(len(self._value), len(self._value[0]) if self._value else 0)))

    def is_square(self) -> bool:
        """Check if tensor is square.

        Returns:
            True if square, False otherwise

        Example:
            >>> if tensor.is_square():
            ...     print("Square tensor")
        """
        rows, cols = self.shape
        return rows == cols

    def __add__(self, other: "TensorQuantity") -> "TensorQuantity":
        """Add tensors.

        Args:
            other: Other tensor

        Returns:
            Resulting tensor

        Example:
            >>> result = tensor1 + tensor2
        """
        return self.add(other)

    def __sub__(self, other: "TensorQuantity") -> "TensorQuantity":
        """Subtract tensors.

        Args:
            other: Other tensor

        Returns:
            Resulting tensor

        Example:
            >>> result = tensor1 - tensor2
        """
        return self.subtract(other)

    def __mul__(self, scalar: float) -> "TensorQuantity":
        """Multiply by scalar.

        Args:
            scalar: Scalar multiplier

        Returns:
            Scaled tensor

        Example:
            >>> result = tensor * 2.0
        """
        return self.scale(scalar)

    def __rmul__(self, scalar: float) -> "TensorQuantity":
        """Multiply by scalar (right side).

        Args:
            scalar: Scalar multiplier

        Returns:
            Scaled tensor

        Example:
            >>> result = 2.0 * tensor
        """
        return self.scale(scalar)

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(tensor)
        """
        return f"TensorQuantity(shape={self.shape}, unit={self._unit.name()}, dimension={self._dimension.name()})"


# Export
__all__ = [
    "TensorQuantity",
]
