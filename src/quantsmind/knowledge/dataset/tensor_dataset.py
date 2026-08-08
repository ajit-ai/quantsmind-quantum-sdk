"""
Tensor Dataset Module

This module provides tensor dataset definitions for the Knowledge package.

Purpose
-------
Provide tensor dataset management with multi-dimensional array support.

Responsibilities
----------------
- Define tensor dataset structure
- Support multi-dimensional tensor data
- Support tensor operations
- Support tensor metadata
- Support tensor validation

Dependencies
------------
typing (standard library)
quantsmind.knowledge.dataset.dataset (dataset)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from quantsmind.knowledge.dataset.dataset import Dataset
from quantsmind.knowledge.enums import DatasetType
from quantsmind.knowledge.exceptions import DatasetError
from quantsmind.knowledge.types import (
    DatasetData,
    DatasetSchema,
    ValidationResult,
)


class TensorDataset(Dataset):
    """Concrete implementation of a tensor dataset.

    This class provides tensor dataset functionality with multi-dimensional array support.

    Attributes:
        _tensors: Tensor records
        _shape: Tensor shape
        _dtype: Tensor data type
        _dimensions: Number of dimensions

    Example:
        >>> dataset = TensorDataset("tensor_data", shape=(10, 10))
        >>> dataset.add_tensor({"data": [[1, 2], [3, 4]]})
    """

    def __init__(
        self,
        name: str,
        shape: Optional[Tuple[int, ...]] = None,
        dtype: str = "float",
        schema: Optional[DatasetSchema] = None,
        data: Optional[DatasetData] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a TensorDataset.

        Args:
            name: Dataset name
            shape: Tensor shape
            dtype: Tensor data type
            schema: Dataset schema
            data: Dataset data
            metadata: Dataset metadata

        Example:
            >>> dataset = TensorDataset("tensor_data", shape=(10, 10))
        """
        super().__init__(
            name=name,
            dataset_type=DatasetType.TENSOR,
            schema=schema,
            data=data,
            metadata=metadata,
        )
        self._shape = shape
        self._dtype = dtype
        self._dimensions = len(shape) if shape else 0
        self._tensors: List[Dict[str, Any]] = []

    @property
    def shape(self) -> Optional[Tuple[int, ...]]:
        """Get the tensor shape.

        Returns:
            Tensor shape

        Example:
            >>> shape = dataset.shape
        """
        return self._shape

    @property
    def dtype(self) -> str:
        """Get the tensor data type.

        Returns:
            Tensor data type

        Example:
            >>> dtype = dataset.dtype
        """
        return self._dtype

    @property
    def dimensions(self) -> int:
        """Get the number of dimensions.

        Returns:
            Number of dimensions

        Example:
            >>> dims = dataset.dimensions
        """
        return self._dimensions

    @property
    def tensors(self) -> List[Dict[str, Any]]:
        """Get the tensors.

        Returns:
            Tensor records

        Example:
            >>> tensors = dataset.tensors
        """
        return self._tensors.copy()

    def add_tensor(self, tensor: Dict[str, Any]) -> None:
        """Add a tensor to the dataset.

        Args:
            tensor: Tensor data

        Raises:
            DatasetError: If tensor is invalid

        Example:
            >>> dataset.add_tensor({"data": [[1, 2], [3, 4]]})
        """
        if not isinstance(tensor, dict):
            raise DatasetError("Tensor must be a dictionary", {"tensor": tensor})

        tensor_data = tensor.get("data")
        if tensor_data is None:
            raise DatasetError("Tensor must have data", {"tensor": tensor})

        # Validate shape if specified
        if self._shape:
            if not self._validate_shape(tensor_data, self._shape):
                raise DatasetError(
                    f"Tensor shape does not match expected shape {self._shape}",
                    {"expected": self._shape, "actual": self._get_shape(tensor_data)},
                )

        self._tensors.append(tensor)
        self._updated_at = self._updated_at

    def add_tensors(self, tensors: List[Dict[str, Any]]) -> None:
        """Add multiple tensors to the dataset.

        Args:
            tensors: Tensor data list

        Example:
            >>> dataset.add_tensors([{"data": [[1, 2]]}, {"data": [[3, 4]]}])
        """
        for tensor in tensors:
            self.add_tensor(tensor)

    def _validate_shape(self, data: Any, expected_shape: Tuple[int, ...]) -> bool:
        """Validate tensor shape.

        Args:
            data: Tensor data
            expected_shape: Expected shape

        Returns:
            True if shape matches

        Example:
            >>> valid = dataset._validate_shape([[1, 2]], (1, 2))
        """
        actual_shape = self._get_shape(data)
        return actual_shape == expected_shape

    def _get_shape(self, data: Any) -> Tuple[int, ...]:
        """Get shape of tensor data.

        Args:
            data: Tensor data

        Returns:
            Shape tuple

        Example:
            >>> shape = dataset._get_shape([[1, 2], [3, 4]])
        """
        if not isinstance(data, (list, tuple)):
            return ()

        shape = []
        current = data
        while isinstance(current, (list, tuple)):
            shape.append(len(current))
            if len(current) > 0:
                current = current[0]
            else:
                break

        return tuple(shape)

    def get_tensor_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """Get tensor by index.

        Args:
            index: Tensor index

        Returns:
            Tensor data or None

        Example:
            >>> tensor = dataset.get_tensor_by_index(0)
        """
        if 0 <= index < len(self._tensors):
            return self._tensors[index]
        return None

    def get_tensors_by_shape(self, shape: Tuple[int, ...]) -> List[Dict[str, Any]]:
        """Get tensors with specific shape.

        Args:
            shape: Target shape

        Returns:
            Tensor records

        Example:
            >>> tensors = dataset.get_tensors_by_shape((2, 2))
        """
        return [
            tensor for tensor in self._tensors
            if self._get_shape(tensor.get("data", [])) == shape
        ]

    def concatenate_tensors(self, axis: int = 0) -> Optional[List[Any]]:
        """Concatenate all tensors along an axis.

        Args:
            axis: Concatenation axis

        Returns:
            Concatenated tensor or None

        Example:
            >>> concatenated = dataset.concatenate_tensors(axis=0)
        """
        if not self._tensors:
            return None

        # Simple concatenation for lists
        result = []
        for tensor in self._tensors:
            result.append(tensor.get("data"))

        return result

    def calculate_tensor_statistics(self, tensor_index: int) -> Dict[str, float]:
        """Calculate statistics for a tensor.

        Args:
            tensor_index: Tensor index

        Returns:
            Statistics dictionary

        Example:
            >>> stats = dataset.calculate_tensor_statistics(0)
        """
        if tensor_index >= len(self._tensors):
            return {}

        tensor_data = self._tensors[tensor_index].get("data")
        if not tensor_data:
            return {}

        # Flatten the tensor
        flat_data = self._flatten_tensor(tensor_data)

        if not flat_data:
            return {}

        numeric_values = [v for v in flat_data if isinstance(v, (int, float))]

        if not numeric_values:
            return {}

        return {
            "count": len(numeric_values),
            "mean": sum(numeric_values) / len(numeric_values),
            "min": min(numeric_values),
            "max": max(numeric_values),
        }

    def _flatten_tensor(self, data: Any) -> List[Any]:
        """Flatten nested tensor data.

        Args:
            data: Tensor data

        Returns:
            Flattened list

        Example:
            >>> flat = dataset._flatten_tensor([[1, 2], [3, 4]])
        """
        if not isinstance(data, (list, tuple)):
            return [data]

        result = []
        for item in data:
            if isinstance(item, (list, tuple)):
                result.extend(self._flatten_tensor(item))
            else:
                result.append(item)

        return result

    def validate(self) -> ValidationResult:
        """Validate the tensor dataset.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = dataset.validate()
        """
        errors = []

        # Validate base dataset
        base_valid, base_errors = super().validate()
        errors.extend(base_errors)

        # Validate tensors
        for i, tensor in enumerate(self._tensors):
            if "data" not in tensor:
                errors.append(f"Tensor {i} missing data")

            # Validate shape
            if self._shape:
                tensor_data = tensor.get("data")
                if tensor_data and not self._validate_shape(tensor_data, self._shape):
                    errors.append(f"Tensor {i} shape mismatch")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dataset definition

        Example:
            >>> data = dataset.to_dict()
        """
        data = super().to_dict()
        data.update({
            "shape": self._shape,
            "dtype": self._dtype,
            "dimensions": self._dimensions,
            "tensors_count": len(self._tensors),
        })
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(dataset)
        """
        return f"TensorDataset(id={self._id}, name={self._name}, shape={self._shape}, dtype={self._dtype}, tensors={len(self._tensors)})"


# Export
__all__ = [
    "TensorDataset",
]
