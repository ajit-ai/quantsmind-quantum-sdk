"""Core QMQ-09 data-domain models.

The module owns the observation, feature and dataset vocabulary consumed by
every other Data layer component:

* :class:`DataFeature` describes one dimension (name, optional bounds and a
  non-negative weight),
* :class:`DataRecord` holds one observation (identifier + per-feature
  values),
* :class:`FeatureVector` is a lightweight immutable numeric vector used by
  distances and data quality,
* :class:`DataSet` is the ordered, deterministic collection that every Data
  problem is built from.

All models are JSON-safe through :meth:`to_dict`/:meth:`from_dict` and are
deterministic: feature and record ordering is preserved and validated at
construction time.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from quantsmind.quantum.data._validation import (
    check_finite,
    check_nonempty_name,
    check_nonnegative,
    check_unique_names,
)
from quantsmind.quantum.data.errors import DataValidationError

__all__ = [
    "DataFeature",
    "DataRecord",
    "FeatureVector",
    "DataSet",
]


@dataclass
class DataFeature:
    """One numeric feature/dimension of a :class:`DataSet`.

    Args:
        name: Unique feature identifier.
        lower_bound: Optional inclusive lower bound for valid values.
        upper_bound: Optional inclusive upper bound for valid values.
        weight: Optional non-negative weight (used by weighted distances and
            data quality).
        kind: Free-form feature kind (e.g. ``"numeric"``).
        description: Free-form description.
        metadata: Free-form metadata (JSON-safe).
    """

    name: str
    lower_bound: float | None = None
    upper_bound: float | None = None
    weight: float = 1.0
    kind: str = "numeric"
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        try:
            check_nonempty_name(self.name, label="feature name")
        except ValueError as exc:
            raise DataValidationError(str(exc)) from exc
        if self.lower_bound is not None:
            try:
                check_finite(self.lower_bound, label=f"lower_bound of feature {self.name!r}")
            except ValueError as exc:
                raise DataValidationError(str(exc)) from exc
        if self.upper_bound is not None:
            try:
                check_finite(self.upper_bound, label=f"upper_bound of feature {self.name!r}")
            except ValueError as exc:
                raise DataValidationError(str(exc)) from exc
        if (
            self.lower_bound is not None
            and self.upper_bound is not None
            and float(self.lower_bound) > float(self.upper_bound)
        ):
            raise DataValidationError(
                f"lower_bound of feature {self.name!r} exceeds its upper_bound"
            )
        try:
            check_nonnegative(self.weight, label=f"weight of feature {self.name!r}")
        except ValueError as exc:
            raise DataValidationError(str(exc)) from exc
        if not self.kind:
            raise DataValidationError(f"kind of feature {self.name!r} cannot be empty")

    def allows(self, value: float) -> bool:
        """Return whether ``value`` respects the optional feature bounds."""
        check_finite(value, label=f"value of feature {self.name!r}")
        if self.lower_bound is not None and float(value) < float(self.lower_bound):
            return False
        return not (self.upper_bound is not None and float(value) > float(self.upper_bound))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "weight": float(self.weight),
            "kind": self.kind,
            "description": self.description,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DataFeature:
        """Rebuild a feature from :meth:`to_dict` output."""
        return cls(
            name=str(data["name"]),
            lower_bound=(
                float(data["lower_bound"]) if data.get("lower_bound") is not None else None
            ),
            upper_bound=(
                float(data["upper_bound"]) if data.get("upper_bound") is not None else None
            ),
            weight=float(data.get("weight", 1.0)),
            kind=str(data.get("kind", "numeric")),
            description=str(data.get("description", "")),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class DataRecord:
    """One observation inside a :class:`DataSet`.

    Args:
        record_id: Unique record identifier.
        values: Feature name -> value mapping.
        metadata: Free-form metadata (JSON-safe).
    """

    record_id: str
    values: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.record_id, str) or not self.record_id.strip():
            raise DataValidationError(
                f"record identifier must be a non-empty string, got {self.record_id!r}"
            )
        for name, value in self.values.items():
            check_finite(value, label=f"value of feature {name!r} in record {self.record_id!r}")

    def value(self, feature_name: str) -> float:
        """Return the value of ``feature_name`` (raises on unknown keys)."""
        try:
            return float(self.values[feature_name])
        except KeyError as exc:
            raise KeyError(
                f"record {self.record_id!r} has no value for feature {feature_name!r}"
            ) from exc

    def as_feature_vector(self, features: list[DataFeature]) -> list[float]:
        """Return values in deterministic ``features`` order.

        Raises:
            DataValidationError: If a feature is missing from the record.
        """
        vector: list[float] = []
        for feature in features:
            if feature.name not in self.values:
                raise DataValidationError(
                    f"record {self.record_id!r} is missing feature {feature.name!r}"
                )
            vector.append(float(self.values[feature.name]))
        return vector

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "record_id": self.record_id,
            "values": {name: float(value) for name, value in self.values.items()},
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DataRecord:
        """Rebuild a record from :meth:`to_dict` output."""
        return cls(
            record_id=str(data["record_id"]),
            values={name: float(value) for name, value in data.get("values", {}).items()},
            metadata=dict(data.get("metadata", {})),
        )


@dataclass(frozen=True)
class FeatureVector:
    """Lightweight immutable numeric feature vector (in feature order).

    Args:
        values: Numeric values in feature order.
        normalization: Free-form normalization metadata (JSON-safe).
    """

    values: tuple[float, ...]
    normalization: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.values:
            raise DataValidationError("a FeatureVector needs at least one value")
        for index, value in enumerate(self.values):
            check_finite(value, label=f"value at index {index}")

    @property
    def dimension(self) -> int:
        """Number of numeric dimensions."""
        return len(self.values)

    def to_list(self) -> list[float]:
        """Return the values as a plain list."""
        return list(self.values)

    @classmethod
    def from_sequence(
        cls, values: Any, *, normalization: dict[str, Any] | None = None
    ) -> FeatureVector:
        """Build a vector from any sequence of finite numbers."""
        if isinstance(values, cls):
            return values
        return cls(
            values=tuple(float(value) for value in values),
            normalization=dict(normalization or {}),
        )

    @classmethod
    def from_record(cls, record: DataRecord, features: list[DataFeature]) -> FeatureVector:
        """Build a vector from a record in deterministic feature order."""
        return cls(values=tuple(record.as_feature_vector(features)))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {"values": list(self.values), "normalization": dict(self.normalization)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FeatureVector:
        """Rebuild a vector from :meth:`to_dict` output."""
        return cls(
            values=tuple(float(value) for value in data.get("values", [])),
            normalization=dict(data.get("normalization", {})),
        )


@dataclass
class DataSet:
    """Ordered collection of features and records.

    Construction enforces unique feature names and unique record identifiers.
    Structural issues (missing/unknown/non-finite values, empty memberships)
    are reported by :meth:`validate` / :meth:`raise_if_invalid` without ever
    being raised at construction time, so partial data can be inspected
    through :func:`quantsmind.quantum.data.quality.assess_data_quality`.

    Deterministic orderings exposed here (``feature_names``, ``record_ids``,
    :meth:`matrix`) are the ordering contract for every Data problem.

    Args:
        name: Dataset identifier.
        features: Ordered feature list.
        records: Ordered record list.
        description: Free-form description.
        metadata: Free-form metadata (JSON-safe).
    """

    name: str
    features: list[DataFeature] = field(default_factory=list)
    records: list[DataRecord] = field(default_factory=list)
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise DataValidationError(f"dataset name must be a non-empty string, got {self.name!r}")
        check_unique_names([feature.name for feature in self.features], label="feature")
        check_unique_names([record.record_id for record in self.records], label="record")

    def __len__(self) -> int:
        """Number of records."""
        return len(self.records)

    def __iter__(self) -> Iterator[DataRecord]:
        """Iterate over records in deterministic order."""
        return iter(self.records)

    @property
    def shape(self) -> tuple[int, int]:
        """Return ``(feature_count, record_count)``."""
        return len(self.features), len(self.records)

    @property
    def feature_names(self) -> list[str]:
        """Return feature names in deterministic order."""
        return [feature.name for feature in self.features]

    @property
    def record_ids(self) -> list[str]:
        """Return record identifiers in deterministic order."""
        return [record.record_id for record in self.records]

    def feature(self, name: str) -> DataFeature:
        """Return the :class:`DataFeature` with ``name``."""
        for feature in self.features:
            if feature.name == name:
                return feature
        raise KeyError(f"dataset {self.name!r} has no feature {name!r}")

    def record(self, record_id: str) -> DataRecord:
        """Return the :class:`DataRecord` with ``record_id``."""
        for record in self.records:
            if record.record_id == record_id:
                return record
        raise KeyError(f"dataset {self.name!r} has no record {record_id!r}")

    def index_of(self, record_id: str) -> int:
        """Return the deterministic record index of ``record_id``."""
        for index, record in enumerate(self.records):
            if record.record_id == record_id:
                return index
        raise KeyError(f"dataset {self.name!r} has no record {record_id!r}")

    def matrix(self) -> list[list[float]]:
        """Return rows (record order) of feature values (feature order).

        Raises:
            DataValidationError: When a record is missing a feature (call
                :meth:`raise_if_invalid` first for friendly issues).
        """
        return [record.as_feature_vector(self.features) for record in self.records]

    def validate(self) -> list[str]:
        """Return deterministic structural issues of the dataset.

        Never raises; :meth:`raise_if_invalid` raises on a non-empty result.
        """
        issues: list[str] = []
        if not self.features:
            issues.append("dataset has no features")
        if not self.records:
            issues.append("dataset has no records")
        if not self.features or not self.records:
            return sorted(issues)
        feature_names = self.feature_names
        for record in self.records:
            record_features = set(record.values)
            feature_set = set(feature_names)
            for name in sorted(feature_set - record_features):
                issues.append(f"record {record.record_id!r} is missing feature {name!r}")
            for name in sorted(record_features - feature_set):
                issues.append(f"record {record.record_id!r} has unknown feature {name!r}")
            for name in feature_names:
                value = record.values.get(name)
                if value is None or not _is_finite(float(value)):
                    issues.append(
                        f"record {record.record_id!r} has a non-finite value for feature {name!r}"
                    )
        return sorted(issues)

    def raise_if_invalid(self) -> None:
        """Raise :class:`DataValidationError` with all structural issues."""
        issues = self.validate()
        if issues:
            raise DataValidationError(f"invalid dataset {self.name!r}: " + "; ".join(issues))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "features": [feature.to_dict() for feature in self.features],
            "records": [record.to_dict() for record in self.records],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DataSet:
        """Rebuild a dataset from :meth:`to_dict` output."""
        return cls(
            name=str(data["name"]),
            description=str(data.get("description", "")),
            features=[DataFeature.from_dict(d) for d in data.get("features", [])],
            records=[DataRecord.from_dict(d) for d in data.get("records", [])],
            metadata=dict(data.get("metadata", {})),
        )


def _is_finite(value: float) -> bool:
    import math

    return math.isfinite(value)
