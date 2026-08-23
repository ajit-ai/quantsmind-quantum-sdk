"""
Tensor Module

This module provides tensor operations for the Mathematics package.
Tensor represents a mathematical tensor with support for common operations.

Purpose
-------
Provide tensor operations for the Mathematics package.

Scientific Meaning
------------------
Tensor represents a mathematical tensor: multi-dimensional arrays used in
quantum mechanics, general relativity, machine learning, and scientific computing.

Responsibilities
----------------
- Support tensor creation
- Enable tensor operations
- Support tensor transformations
- Handle tensor validation

Dependencies
------------
typing (standard library)
quantsmind.math.exceptions (exception hierarchy)
quantsmind.math.types (type definitions)
quantsmind.math.validation (validation functions)

Future Extensions
-----------------
- GPU-accelerated operations
- Sparse tensors
- Complex tensor operations
- Tensor views
"""

from __future__ import annotations

import logging
from typing import Any, List, Tuple, Union

from quantsmind.math.exceptions import (
    DimensionError,
    InvalidOperationError,
    ShapeError,
)
from quantsmind.math.exceptions import (
    IndexError as MathIndexError,
)
from quantsmind.math.types import Scalar, Shape, TensorShape

logger = logging.getLogger(__name__)


class Tensor:
    """Concrete implementation of a mathematical tensor.

    This class provides a comprehensive tensor representation with support for
    common tensor operations including addition, subtraction, multiplication,
    contraction, and reshaping.

    Scientific Meaning
    ------------------
    In scientific computing, tensors represent multi-dimensional arrays used in
    quantum mechanics (state vectors, operators), general relativity (metric tensors),
    machine learning (weights, activations), and other advanced applications.

    Attributes:
        _data: Tensor data (nested lists)
        _shape: Tensor shape

    Example:
        >>> t = Tensor([[[1.0, 2.0], [3.0, 4.0]], [[5.0, 6.0], [7.0, 8.0]]])
        >>> print(f"Shape: {t.shape}")
    """

    def __init__(self, data: Any) -> None:
        """Initialize a Tensor.

        Args:
            data: Tensor data (nested lists)

        Raises:
            ValueError: If data is invalid

        Example:
            >>> t = Tensor([[[1.0, 2.0], [3.0, 4.0]], [[5.0, 6.0], [7.0, 8.0]]])
        """
        self._data = data
        self._shape = self._infer_shape(data)
        logger.debug(f"Created tensor of shape {self._shape}")

    def _infer_shape(self, data: Any) -> Shape:
        """Infer the shape of nested data.

        Args:
            data: Nested data

        Returns:
            Shape tuple
        """
        if isinstance(data, (int, float, complex)):
            return ()
        if isinstance(data, (list, tuple)):
            if len(data) == 0:
                return (0,)
            inner_shape = self._infer_shape(data[0])
            for item in data:
                if self._infer_shape(item) != inner_shape:
                    raise ValueError("Inconsistent tensor dimensions")
            return (len(data),) + inner_shape
        raise ValueError(f"Invalid tensor data type: {type(data)}")

    @property
    def shape(self) -> Shape:
        """Get the tensor shape.

        Returns:
            Shape tuple

        Example:
            >>> print(f"Shape: {tensor.shape}")
        """
        return self._shape

    @property
    def rank(self) -> int:
        """Get the tensor rank (number of dimensions).

        Returns:
            Tensor rank

        Example:
            >>> print(f"Rank: {tensor.rank}")
        """
        return len(self._shape)

    @property
    def data(self) -> Any:
        """Get the tensor data.

        Returns:
            Tensor data

        Example:
            >>> print(f"Data: {tensor.data}")
        """
        return self._data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(tensor)
        """
        return f"Tensor(shape={self._shape})"

    def __str__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> str(tensor)
        """
        return str(self._data)

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> tensor1 == tensor2
        """
        if not isinstance(other, Tensor):
            return False
        return self._shape == other._shape and self._data == other._data

    def __hash__(self) -> int:
        """Return hash.

        Returns:
            Hash value

        Example:
            >>> hash(tensor)
        """
        return hash((self._shape, str(self._data)))

    def __add__(self, other: Tensor) -> Tensor:
        """Add two tensors.

        Args:
            other: Other tensor

        Returns:
            Sum tensor

        Raises:
            ShapeError: If shapes don't match

        Example:
            >>> result = tensor1 + tensor2
        """
        if self._shape != other._shape:
            raise ShapeError(f"Shape mismatch: {self._shape} vs {other._shape}")
        return Tensor(self._add_data(self._data, other._data))

    def _add_data(self, a: Any, b: Any) -> Any:
        """Recursively add nested data.

        Args:
            a: First data
            b: Second data

        Returns:
            Sum data
        """
        if isinstance(a, (int, float, complex)):
            return a + b
        return [self._add_data(ai, bi) for ai, bi in zip(a, b, strict=False)]

    def __sub__(self, other: Tensor) -> Tensor:
        """Subtract two tensors.

        Args:
            other: Other tensor

        Returns:
            Difference tensor

        Raises:
            ShapeError: If shapes don't match

        Example:
            >>> result = tensor1 - tensor2
        """
        if self._shape != other._shape:
            raise ShapeError(f"Shape mismatch: {self._shape} vs {other._shape}")
        return Tensor(self._sub_data(self._data, other._data))

    def _sub_data(self, a: Any, b: Any) -> Any:
        """Recursively subtract nested data.

        Args:
            a: First data
            b: Second data

        Returns:
            Difference data
        """
        if isinstance(a, (int, float, complex)):
            return a - b
        return [self._sub_data(ai, bi) for ai, bi in zip(a, b, strict=False)]

    def __mul__(self, scalar: Scalar) -> Tensor:
        """Multiply tensor by scalar.

        Args:
            scalar: Scalar value

        Returns:
            Scaled tensor

        Example:
            >>> result = tensor * 2.0
        """
        return Tensor(self._mul_data(self._data, scalar))

    def _mul_data(self, data: Any, scalar: Scalar) -> Any:
        """Recursively multiply nested data by scalar.

        Args:
            data: Data to multiply
            scalar: Scalar value

        Returns:
            Scaled data
        """
        if isinstance(data, (int, float, complex)):
            return data * scalar
        return [self._mul_data(d, scalar) for d in data]

    def __rmul__(self, scalar: Scalar) -> Tensor:
        """Multiply scalar by tensor.

        Args:
            scalar: Scalar value

        Returns:
            Scaled tensor

        Example:
            >>> result = 2.0 * tensor
        """
        return self.__mul__(scalar)

    def reshape(self, new_shape: Shape) -> Tensor:
        """Reshape the tensor.

        Args:
            new_shape: New shape

        Returns:
            Reshaped tensor

        Raises:
            ShapeError: If new shape is incompatible

        Example:
            >>> reshaped = tensor.reshape((8,))
        """
        flat = self._flatten(self._data)
        if len(flat) != self._total_size(new_shape):
            raise ShapeError(f"Cannot reshape {self._shape} to {new_shape}")
        return Tensor(self._unflatten(flat, new_shape))

    def _flatten(self, data: Any) -> list[Scalar]:
        """Flatten nested data to a list.

        Args:
            data: Nested data

        Returns:
            Flattened list
        """
        if isinstance(data, (int, float, complex)):
            return [data]
        result = []
        for item in data:
            result.extend(self._flatten(item))
        return result

    def _unflatten(self, flat: list[Scalar], shape: Shape) -> Any:
        """Unflatten a list to nested data.

        Args:
            flat: Flattened list
            shape: Target shape

        Returns:
            Nested data
        """
        if not shape:
            return flat[0]
        size = self._total_size(shape[1:])
        return [self._unflatten(flat[i*size:(i+1)*size], shape[1:]) for i in range(shape[0])]

    def _total_size(self, shape: Shape) -> int:
        """Calculate total size from shape.

        Args:
            shape: Shape tuple

        Returns:
            Total size
        """
        if not shape:
            return 1
        size = 1
        for dim in shape:
            size *= dim
        return size

    def transpose(self, axes: tuple[int, ...] | None = None) -> Tensor:
        """Transpose the tensor.

        Args:
            axes: Axes to transpose (None reverses all axes)

        Returns:
            Transposed tensor

        Example:
            >>> transposed = tensor.transpose()
        """
        if axes is None:
            axes = tuple(range(self.rank - 1, -1, -1))
        if len(axes) != self.rank:
            raise ShapeError(f"Number of axes must match rank: {len(axes)} vs {self.rank}")
        return Tensor(self._transpose_data(self._data, axes))

    def _transpose_data(self, data: Any, axes: tuple[int, ...]) -> Any:
        """Recursively transpose nested data.

        Args:
            data: Nested data
            axes: Axes to transpose

        Returns:
            Transposed data
        """
        if self.rank == 0:
            return data
        if self.rank == 1:
            return data
        # Simplified implementation for 2D case
        if self.rank == 2:
            return [[data[j][i] for j in range(len(data))] for i in range(len(data[0]))]
        raise NotImplementedError("Transpose for tensors with rank > 2 not yet implemented")

    def contract(self, axis1: int, axis2: int) -> Tensor:
        """Contract two axes of the tensor.

        Args:
            axis1: First axis to contract
            axis2: Second axis to contract

        Returns:
            Contracted tensor

        Example:
            >>> contracted = tensor.contract(0, 1)
        """
        if axis1 >= self.rank or axis2 >= self.rank:
            raise DimensionError(f"Axis out of bounds: {axis1}, {axis2} vs rank {self.rank}")
        if axis1 == axis2:
            raise DimensionError("Cannot contract the same axis")
        # Simplified implementation
        raise NotImplementedError("Tensor contraction not yet implemented")

    def copy(self) -> Tensor:
        """Create a copy of the tensor.

        Returns:
            Copy of tensor

        Example:
            >>> copy = tensor.copy()
        """
        return Tensor(self._data)


class TensorProduct:
    """Tensor product operation.

    This class represents the tensor product operation between tensors.

    Example:
        >>> product = TensorProduct()
        >>> result = product.apply(tensor1, tensor2)
    """

    def apply(self, tensor1: Tensor, tensor2: Tensor) -> Tensor:
        """Apply tensor product.

        Args:
            tensor1: First tensor
            tensor2: Second tensor

        Returns:
            Tensor product

        Example:
            >>> result = product.apply(tensor1, tensor2)
        """
        # Simplified implementation
        raise NotImplementedError("Tensor product not yet implemented")


class TensorSpace:
    """Tensor space representation.

    This class represents a space of tensors with a given shape.

    Example:
        >>> space = TensorSpace((3, 3))
    """

    def __init__(self, shape: Shape) -> None:
        """Initialize a TensorSpace.

        Args:
            shape: Shape of tensors in the space

        Example:
            >>> space = TensorSpace((3, 3))
        """
        self._shape = shape

    @property
    def shape(self) -> Shape:
        """Get the space shape.

        Returns:
            Shape tuple

        Example:
            >>> print(f"Shape: {space.shape}")
        """
        return self._shape

    @property
    def dimension(self) -> int:
        """Get the space dimension.

        Returns:
            Total dimension

        Example:
            >>> print(f"Dimension: {space.dimension}")
        """
        dim = 1
        for s in self._shape:
            dim *= s
        return dim


class TensorOperator:
    """Tensor operator representation.

    This class represents an operator that acts on tensors.

    Example:
        >>> operator = TensorOperator()
        >>> result = operator.apply(tensor)
    """

    def apply(self, tensor: Tensor) -> Tensor:
        """Apply the operator to a tensor.

        Args:
            tensor: Input tensor

        Returns:
            Output tensor

        Example:
            >>> result = operator.apply(tensor)
        """
        raise NotImplementedError("Tensor operator not yet implemented")


# Export
__all__ = [
    "Tensor",
    "TensorProduct",
    "TensorSpace",
    "TensorOperator",
]
