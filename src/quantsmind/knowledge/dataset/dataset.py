"""
Dataset Module

This module provides dataset definitions for the Knowledge package.

Purpose
-------
Provide dataset management and operations.

Responsibilities
----------------
- Define dataset structure
- Support dataset operations
- Support dataset validation
- Support dataset metadata

Dependencies
------------
typing (standard library)
datetime (standard library)
uuid (standard library)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.interfaces (knowledge interfaces)
quantsmind.knowledge.types (knowledge types)
quantsmind.knowledge.metadata (metadata)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from quantsmind.knowledge.enums import DatasetType
from quantsmind.knowledge.exceptions import DatasetError
from quantsmind.knowledge.interfaces import IDataset
from quantsmind.knowledge.metadata.metadata import KnowledgeMetadata
from quantsmind.knowledge.types import (
    DatasetData,
    DatasetID,
    DatasetSchema,
    ValidationResult,
)


class Dataset(IDataset):
    """Concrete implementation of a dataset.

    This class provides dataset functionality.

    Attributes:
        _id: Dataset ID
        _name: Dataset name
        _dataset_type: Dataset type
        _schema: Dataset schema
        _data: Dataset data
        _metadata: Dataset metadata
        _created_at: Creation timestamp
        _updated_at: Update timestamp

    Example:
        >>> dataset = Dataset("my_dataset", DatasetType.STRUCTURED)
        >>> dataset.add_record({"key": "value"})
    """

    def __init__(
        self,
        name: str,
        dataset_type: DatasetType = DatasetType.STRUCTURED,
        schema: DatasetSchema | None = None,
        data: DatasetData | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Dataset.

        Args:
            name: Dataset name
            dataset_type: Dataset type
            schema: Dataset schema
            data: Dataset data
            metadata: Dataset metadata

        Example:
            >>> dataset = Dataset("my_dataset", DatasetType.STRUCTURED)
        """
        self._id: DatasetID = uuid4()
        self._name = name
        self._dataset_type = dataset_type
        self._schema = schema or {}
        self._data: DatasetData = data if data is not None else []
        self._metadata = KnowledgeMetadata(metadata or {})
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()

    @property
    def id(self) -> DatasetID:
        """Get the dataset ID.

        Returns:
            Dataset ID

        Example:
            >>> dataset_id = dataset.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the dataset name.

        Returns:
            Dataset name

        Example:
            >>> dataset_name = dataset.name
        """
        return self._name

    @property
    def dataset_type(self) -> DatasetType:
        """Get the dataset type.

        Returns:
            Dataset type

        Example:
            >>> dtype = dataset.dataset_type
        """
        return self._dataset_type

    @property
    def schema(self) -> DatasetSchema:
        """Get the dataset schema.

        Returns:
            Dataset schema

        Example:
            >>> schema = dataset.schema
        """
        return self._schema

    @property
    def data(self) -> DatasetData:
        """Get the dataset data.

        Returns:
            Dataset data

        Example:
            >>> data = dataset.data
        """
        return self._data

    @property
    def size(self) -> int:
        """Get the dataset size.

        Returns:
            Dataset size (number of records)

        Example:
            >>> size = dataset.size
        """
        if isinstance(self._data, (list, dict)):
            return len(self._data)
        return 0

    @property
    def metadata(self) -> KnowledgeMetadata:
        """Get the dataset metadata.

        Returns:
            Dataset metadata

        Example:
            >>> metadata = dataset.metadata
        """
        return self._metadata

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp.

        Returns:
            Creation timestamp

        Example:
            >>> created = dataset.created_at
        """
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get the update timestamp.

        Returns:
            Update timestamp

        Example:
            >>> updated = dataset.updated_at
        """
        return self._updated_at

    def add_record(self, record: dict[str, Any]) -> None:
        """Add a record to the dataset.

        Args:
            record: Record to add

        Raises:
            DatasetError: If record is invalid

        Example:
            >>> dataset.add_record({"key": "value"})
        """
        if not isinstance(record, dict):
            raise DatasetError("Record must be a dictionary", {"record": record})

        if isinstance(self._data, list):
            self._data.append(record)
        elif isinstance(self._data, dict):
            record_id = record.get("id", str(uuid4()))
            self._data[record_id] = record

        self._updated_at = datetime.utcnow()

    def add_records(self, records: list[dict[str, Any]]) -> None:
        """Add multiple records to the dataset.

        Args:
            records: Records to add

        Example:
            >>> dataset.add_records([{"key": "value1"}, {"key": "value2"}])
        """
        for record in records:
            self.add_record(record)

    def get_record(self, record_id: str) -> dict[str, Any] | None:
        """Get a record from the dataset.

        Args:
            record_id: Record ID

        Returns:
            Record or None

        Example:
            >>> record = dataset.get_record("rec_001")
        """
        if isinstance(self._data, list):
            for record in self._data:
                if record.get("id") == record_id:
                    return record
        elif isinstance(self._data, dict):
            return self._data.get(record_id)
        return None

    def query(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        """Query the dataset.

        Args:
            query: Query parameters

        Returns:
            Query results

        Example:
            >>> results = dataset.query({"key": "value"})
        """
        results = []
        data_list = self._data if isinstance(self._data, list) else list(self._data.values())

        for record in data_list:
            match = True
            for key, value in query.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                results.append(record)

        return results

    def filter(self, predicate: callable) -> list[dict[str, Any]]:
        """Filter dataset records.

        Args:
            predicate: Filter predicate function

        Returns:
            Filtered records

        Example:
            >>> results = dataset.filter(lambda x: x["value"] > 10)
        """
        data_list = self._data if isinstance(self._data, list) else list(self._data.values())
        return [record for record in data_list if predicate(record)]

    def sort(self, key: str, reverse: bool = False) -> list[dict[str, Any]]:
        """Sort dataset records.

        Args:
            key: Sort key
            reverse: Sort in reverse order

        Returns:
            Sorted records

        Example:
            >>> results = dataset.sort("value")
        """
        data_list = self._data if isinstance(self._data, list) else list(self._data.values())
        return sorted(data_list, key=lambda x: x.get(key, 0), reverse=reverse)

    def validate(self) -> ValidationResult:
        """Validate the dataset.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = dataset.validate()
        """
        errors = []

        if not self._name:
            errors.append("Dataset name cannot be empty")

        if not isinstance(self._data, (list, dict)):
            errors.append("Dataset data must be a list or dictionary")

        if self._schema and not isinstance(self._schema, dict):
            errors.append("Dataset schema must be a dictionary")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dataset definition

        Example:
            >>> data = dataset.to_dict()
        """
        return {
            "id": str(self._id),
            "name": self._name,
            "dataset_type": self._dataset_type.value,
            "schema": self._schema,
            "size": self.size,
            "metadata": self._metadata.to_dict(),
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(dataset)
        """
        return f"Dataset(id={self._id}, name={self._name}, type={self._dataset_type.value}, size={self.size})"


# Export
__all__ = [
    "Dataset",
]
