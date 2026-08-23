"""
Dataset Registry Module

This module provides dataset registry functionality for the Knowledge package.

Purpose
-------
Provide dataset registration and management.

Responsibilities
----------------
- Register datasets
- Retrieve datasets
- List datasets
- Remove datasets
- Validate datasets

Dependencies
------------
typing (standard library)
quantsmind.knowledge.dataset.dataset (dataset)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.knowledge.dataset.dataset import Dataset
from quantsmind.knowledge.exceptions import DatasetError
from quantsmind.knowledge.types import DatasetID, ValidationResult


class DatasetRegistry:
    """Dataset registry for managing datasets.

    This class provides dataset registration and management functionality.

    Attributes:
        _datasets: Registered datasets
        _metadata: Registry metadata

    Example:
        >>> registry = DatasetRegistry()
        >>> registry.register(dataset)
    """

    def __init__(self) -> None:
        """Initialize a DatasetRegistry.

        Example:
            >>> registry = DatasetRegistry()
        """
        self._datasets: dict[DatasetID, Dataset] = {}
        self._metadata: dict[str, Any] = {}

    def register(self, dataset: Dataset) -> None:
        """Register a dataset.

        Args:
            dataset: Dataset to register

        Raises:
            DatasetError: If dataset already registered

        Example:
            >>> registry.register(dataset)
        """
        dataset_id = dataset.id
        if dataset_id in self._datasets:
            raise DatasetError("Dataset already registered", {"dataset_id": dataset_id})

        self._datasets[dataset_id] = dataset

    def unregister(self, dataset_id: DatasetID) -> bool:
        """Unregister a dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            True if unregistered

        Example:
            >>> unregistered = registry.unregister(dataset_id)
        """
        if dataset_id in self._datasets:
            del self._datasets[dataset_id]
            return True
        return False

    def get(self, dataset_id: DatasetID) -> Dataset | None:
        """Get a registered dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            Dataset or None

        Example:
            >>> dataset = registry.get(dataset_id)
        """
        return self._datasets.get(dataset_id)

    def get_by_name(self, name: str) -> Dataset | None:
        """Get a dataset by name.

        Args:
            name: Dataset name

        Returns:
            Dataset or None

        Example:
            >>> dataset = registry.get_by_name("my_dataset")
        """
        for dataset in self._datasets.values():
            if dataset.name == name:
                return dataset
        return None

    def list_all(self) -> list[Dataset]:
        """List all registered datasets.

        Returns:
            List of datasets

        Example:
            >>> datasets = registry.list_all()
        """
        return list(self._datasets.values())

    def list_by_type(self, dataset_type: str) -> list[Dataset]:
        """List datasets by type.

        Args:
            dataset_type: Dataset type

        Returns:
            List of datasets

        Example:
            >>> datasets = registry.list_by_type("structured")
        """
        return [
            dataset for dataset in self._datasets.values()
            if dataset.dataset_type.value == dataset_type
        ]

    def count(self) -> int:
        """Get the number of registered datasets.

        Returns:
            Number of datasets

        Example:
            >>> count = registry.count()
        """
        return len(self._datasets)

    def exists(self, dataset_id: DatasetID) -> bool:
        """Check if a dataset is registered.

        Args:
            dataset_id: Dataset ID

        Returns:
            True if registered

        Example:
            >>> if registry.exists(dataset_id):
            ...     print("Dataset exists")
        """
        return dataset_id in self._datasets

    def validate_all(self) -> ValidationResult:
        """Validate all registered datasets.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = registry.validate_all()
        """
        errors = []

        for dataset_id, dataset in self._datasets.items():
            is_valid, dataset_errors = dataset.validate()
            if not is_valid:
                errors.extend([f"Dataset {dataset_id}: {err}" for err in dataset_errors])

        return (len(errors) == 0, errors)

    def clear(self) -> None:
        """Clear all registered datasets.

        Example:
            >>> registry.clear()
        """
        self._datasets.clear()

    def to_dict(self) -> dict[str, Any]:
        """Convert registry to dictionary.

        Returns:
            Registry state

        Example:
            >>> data = registry.to_dict()
        """
        return {
            "dataset_count": len(self._datasets),
            "dataset_ids": [str(did) for did in self._datasets],
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(registry)
        """
        return f"DatasetRegistry(datasets={len(self._datasets)})"


# Export
__all__ = [
    "DatasetRegistry",
]
