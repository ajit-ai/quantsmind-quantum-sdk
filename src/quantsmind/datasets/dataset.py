"""In-memory dataset foundation.

Records with schema validation, deterministic splitting and batching,
row transformations, column statistics, and serialization boundaries.
Deterministic (insertion-ordered) and dependency-free.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterator
from typing import Any

__all__ = [
    "Schema",
    "Dataset",
    "SchemaError",
    "describe_numeric",
]


class SchemaError(ValueError):
    """Raised when a record violates its schema."""


class Schema:
    """Record schema: field name -> expected type plus required fields.

    Args:
        fields: Field name -> expected Python type.
        required: Required field names (defaults to all fields).
    """

    def __init__(
        self, fields: dict[str, type], required: list[str] | None = None
    ) -> None:
        """Initialize the schema."""
        if not fields:
            raise ValueError("schema must declare at least one field")
        self._fields = dict(fields)
        self._required = list(required) if required is not None else list(fields)
        unknown = sorted(set(self._required) - set(self._fields))
        if unknown:
            raise ValueError(f"required fields not declared: {unknown}")

    @property
    def fields(self) -> dict[str, type]:
        """Declared fields (copy)."""
        return dict(self._fields)

    @property
    def required(self) -> list[str]:
        """Required field names (copy)."""
        return list(self._required)

    def validate(self, record: dict[str, Any]) -> list[str]:
        """Return a list of violations (empty when valid)."""
        errors = []
        for name in self._required:
            if name not in record:
                errors.append(f"missing required field: {name!r}")
        for name, value in record.items():
            expected = self._fields.get(name)
            if expected is None:
                errors.append(f"unknown field: {name!r}")
            elif not isinstance(value, expected) or (
                isinstance(value, bool) and expected is not bool
            ):
                errors.append(
                    f"field {name!r} must be {expected.__name__}, "
                    f"got {type(value).__name__}"
                )
        return errors

    def raise_if_invalid(self, record: dict[str, Any]) -> None:
        """Raise :class:`SchemaError` on the first violation.

        Raises:
            SchemaError: If the record violates the schema.
        """
        errors = self.validate(record)
        if errors:
            raise SchemaError("; ".join(errors))


def describe_numeric(values: list[float]) -> dict[str, float]:
    """Count/mean/min/max/std of a numeric column (population std).

    Raises:
        ValueError: For empty input or non-finite values.
    """
    if not values:
        raise ValueError("values must not be empty")
    numbers = [float(value) for value in values]
    if not all(math.isfinite(value) for value in numbers):
        raise ValueError("values must all be finite")
    count = len(numbers)
    mean = sum(numbers) / count
    variance = sum((value - mean) ** 2 for value in numbers) / count
    return {
        "count": float(count),
        "mean": mean,
        "min": min(numbers),
        "max": max(numbers),
        "std": math.sqrt(variance),
    }


class Dataset:
    """An ordered, schema-validated collection of records.

    Args:
        schema: Record schema enforced on every added record.
        name: Dataset label.
    """

    def __init__(self, schema: Schema, name: str = "dataset") -> None:
        """Initialize an empty dataset."""
        self._schema = schema
        self._name = name
        self._records: list[dict[str, Any]] = []

    @property
    def name(self) -> str:
        """Dataset label."""
        return self._name

    @property
    def schema(self) -> Schema:
        """Record schema."""
        return self._schema

    def __len__(self) -> int:
        """Number of records."""
        return len(self._records)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """Iterate records in insertion order."""
        return iter(self._records)

    def add(self, record: dict[str, Any]) -> None:
        """Validate and append a record (stores a copy).

        Raises:
            SchemaError: If the record violates the schema.
        """
        self._schema.raise_if_invalid(record)
        self._records.append(dict(record))

    def extend(self, records: list[dict[str, Any]]) -> None:
        """Validate and append many records atomically.

        Raises:
            SchemaError: If any record is invalid (nothing is appended).
        """
        for record in records:
            self._schema.raise_if_invalid(record)
        self._records.extend(dict(record) for record in records)

    def split(self, train_fraction: float) -> tuple[Dataset, Dataset]:
        """Deterministically split into (train, test) by order.

        Raises:
            ValueError: If the fraction is not within (0, 1).
        """
        if not 0.0 < train_fraction < 1.0:
            raise ValueError(f"train_fraction must be within (0, 1), got {train_fraction!r}")
        cut = int(len(self._records) * train_fraction)
        train = Dataset(self._schema, name=f"{self._name}/train")
        test = Dataset(self._schema, name=f"{self._name}/test")
        train.extend(self._records[:cut])
        test.extend(self._records[cut:])
        return train, test

    def batch(self, size: int) -> list[list[dict[str, Any]]]:
        """Split records into consecutive batches of ``size``.

        Raises:
            ValueError: If size is not positive.
        """
        if size <= 0:
            raise ValueError(f"batch size must be positive, got {size!r}")
        return [self._records[index : index + size] for index in range(0, len(self._records), size)]

    def transform(self, func: Callable[[dict[str, Any]], dict[str, Any]]) -> Dataset:
        """Build a new dataset by applying ``func`` to each record.

        The transform must return schema-valid records.

        Raises:
            SchemaError: If any transformed record is invalid.
        """
        transformed = Dataset(self._schema, name=f"{self._name}/transformed")
        transformed.extend([func(record) for record in self._records])
        return transformed

    def column(self, name: str) -> list[Any]:
        """Values of one field across records (KeyError if unknown)."""
        if name not in self._schema.fields:
            raise KeyError(f"unknown field: {name!r}")
        return [record.get(name) for record in self._records]

    def describe(self, name: str) -> dict[str, float]:
        """Numeric summary of one column (see :func:`describe_numeric`)."""
        return describe_numeric([float(value) for value in self.column(name) if value is not None])

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "name": self._name,
            "fields": {name: tp.__name__ for name, tp in self._schema.fields.items()},
            "records": [dict(record) for record in self._records],
        }

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], schema: Schema
    ) -> Dataset:
        """Rebuild a dataset (records re-validated against ``schema``)."""
        dataset = cls(schema, name=str(data.get("name", "dataset")))
        dataset.extend(list(data.get("records", [])))
        return dataset
