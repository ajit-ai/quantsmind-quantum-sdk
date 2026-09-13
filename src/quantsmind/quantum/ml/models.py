"""Core QMQ-10 AI/ML domain models.

The module owns the small/structured ML vocabulary consumed by every other ML
layer component:

* :class:`MLFeature` describes one numeric dimension of the ML dataset,
* :class:`MLRecord` holds one observation (identifier + per-feature values +
  a numeric target),
* :class:`MLDataSet` is the ordered, deterministic collection that the
  fitting, feature-selection and clustering problems are built from,
* :class:`MLModelCandidate` carries caller-supplied validation loss and
  complexity penalty of one model-selection candidate,
* :class:`MLHyperparameter` / :class:`MLHyperparameterChoice` carry the
  deterministic finite hyperparameter space with per-choice gains.

All models are JSON-safe through :meth:`to_dict`/:meth:`from_dict` and are
deterministic: feature and record ordering is preserved and validated at
construction time.  Nothing here performs training, inference or
hyperparameter search — the data is supplied, the search is the quantum
optimization built by the formulation layer.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from quantsmind.quantum.ml._validation import (
    check_finite,
    check_nonempty_name,
    check_nonnegative,
    check_unique_names,
)
from quantsmind.quantum.ml.errors import MLValidationError

__all__ = [
    "MLFeature",
    "MLRecord",
    "MLDataSet",
    "MLModelCandidate",
    "MLHyperparameter",
    "MLHyperparameterChoice",
]


@dataclass
class MLFeature:
    """One numeric feature/dimension of an :class:`MLDataSet`.

    Args:
        name: Unique feature identifier.
        kind: Free-form feature kind (e.g. ``"numeric"``).
        description: Free-form description.
        metadata: Free-form metadata (JSON-safe).
    """

    name: str
    kind: str = "numeric"
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        try:
            check_nonempty_name(self.name, label="feature name")
        except MLValidationError as exc:
            raise MLValidationError(str(exc)) from exc
        if not self.kind:
            raise MLValidationError(f"kind of feature {self.name!r} cannot be empty")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "kind": self.kind,
            "description": self.description,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MLFeature:
        """Rebuild a feature from :meth:`to_dict` output."""
        return cls(
            name=str(data["name"]),
            kind=str(data.get("kind", "numeric")),
            description=str(data.get("description", "")),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class MLRecord:
    """One observation inside an :class:`MLDataSet`.

    Args:
        record_id: Unique record identifier.
        values: Feature name -> value mapping.
        target: Numeric target value (a class index for classification, a
            continuous response for regression).
        metadata: Free-form metadata (JSON-safe).
    """

    record_id: str
    values: dict[str, float] = field(default_factory=dict)
    target: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.record_id, str) or not self.record_id.strip():
            raise MLValidationError(
                f"record identifier must be a non-empty string, got {self.record_id!r}"
            )
        for name, value in self.values.items():
            check_finite(value, label=f"value of feature {name!r} in record {self.record_id!r}")
        check_finite(self.target, label=f"target of record {self.record_id!r}")

    def value(self, feature_name: str) -> float:
        """Return the value of ``feature_name`` (raises on unknown keys)."""
        try:
            return float(self.values[feature_name])
        except KeyError as exc:
            raise KeyError(
                f"record {self.record_id!r} has no value for feature {feature_name!r}"
            ) from exc

    def as_feature_vector(self, features: list[MLFeature]) -> list[float]:
        """Return values in deterministic ``features`` order.

        Raises:
            MLValidationError: If a feature is missing from the record.
        """
        vector: list[float] = []
        for feature in features:
            if feature.name not in self.values:
                raise MLValidationError(
                    f"record {self.record_id!r} is missing feature {feature.name!r}"
                )
            vector.append(float(self.values[feature.name]))
        return vector

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "record_id": self.record_id,
            "values": {name: float(value) for name, value in self.values.items()},
            "target": float(self.target),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MLRecord:
        """Rebuild a record from :meth:`to_dict` output."""
        return cls(
            record_id=str(data["record_id"]),
            values={name: float(value) for name, value in data.get("values", {}).items()},
            target=float(data.get("target", 0.0)),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class MLDataSet:
    """Ordered collection of :class:`MLFeature` and :class:`MLRecord`.

    Construction enforces unique feature names and unique record identifiers.
    Structural issues (missing/unknown/non-finite values, empty memberships)
    are reported by :meth:`validate` / :meth:`raise_if_invalid` without ever
    being raised at construction time.

    Deterministic orderings exposed here (``feature_names``, ``record_ids``,
    :meth:`matrix`) are the ordering contract for every ML problem.

    Args:
        name: Dataset identifier.
        features: Ordered feature list.
        records: Ordered record list.
        description: Free-form description.
        metadata: Free-form metadata (JSON-safe).
    """

    name: str
    features: list[MLFeature] = field(default_factory=list)
    records: list[MLRecord] = field(default_factory=list)
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise MLValidationError(f"dataset name must be a non-empty string, got {self.name!r}")
        check_unique_names([feature.name for feature in self.features], label="feature")
        check_unique_names([record.record_id for record in self.records], label="record")

    def __len__(self) -> int:
        """Number of records."""
        return len(self.records)

    def __iter__(self) -> Iterator[MLRecord]:
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

    def feature(self, name: str) -> MLFeature:
        """Return the :class:`MLFeature` with ``name``."""
        for feature in self.features:
            if feature.name == name:
                return feature
        raise KeyError(f"dataset {self.name!r} has no feature {name!r}")

    def record(self, record_id: str) -> MLRecord:
        """Return the :class:`MLRecord` with ``record_id``."""
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

    def targets(self) -> list[float]:
        """Return target values in deterministic record order."""
        return [float(record.target) for record in self.records]

    def matrix(self) -> list[list[float]]:
        """Return rows (record order) of feature values (feature order).

        Raises:
            MLValidationError: When a record is missing a feature (call
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
        """Raise :class:`MLValidationError` with all structural issues."""
        issues = self.validate()
        if issues:
            raise MLValidationError(f"invalid ML dataset {self.name!r}: " + "; ".join(issues))

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
    def from_dict(cls, data: dict[str, Any]) -> MLDataSet:
        """Rebuild a dataset from :meth:`to_dict` output."""
        return cls(
            name=str(data["name"]),
            description=str(data.get("description", "")),
            features=[MLFeature.from_dict(d) for d in data.get("features", [])],
            records=[MLRecord.from_dict(d) for d in data.get("records", [])],
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class MLModelCandidate:
    """One model-selection candidate with caller-supplied validation scores.

    Args:
        model_id: Unique candidate identifier.
        validation_loss: Caller-supplied candidate validation loss (must be
            finite and non-negative).
        complexity_penalty: Caller-supplied complexity penalty (must be finite
            and non-negative).
        description: Free-form description.
        metadata: Free-form metadata (JSON-safe).
    """

    model_id: str
    validation_loss: float = 0.0
    complexity_penalty: float = 0.0
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        try:
            check_nonempty_name(self.model_id, label="model id")
        except MLValidationError as exc:
            raise MLValidationError(str(exc)) from exc
        try:
            check_nonnegative(self.validation_loss, label=f"validation loss of {self.model_id!r}")
            check_nonnegative(
                self.complexity_penalty, label=f"complexity penalty of {self.model_id!r}"
            )
        except MLValidationError as exc:
            raise MLValidationError(str(exc)) from exc

    def objective(self) -> float:
        """Return ``validation_loss + complexity_penalty``."""
        return float(self.validation_loss) + float(self.complexity_penalty)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "model_id": self.model_id,
            "validation_loss": float(self.validation_loss),
            "complexity_penalty": float(self.complexity_penalty),
            "description": self.description,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MLModelCandidate:
        """Rebuild a candidate from :meth:`to_dict` output."""
        return cls(
            model_id=str(data["model_id"]),
            validation_loss=float(data.get("validation_loss", 0.0)),
            complexity_penalty=float(data.get("complexity_penalty", 0.0)),
            description=str(data.get("description", "")),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class MLHyperparameterChoice:
    """One choice of an :class:`MLHyperparameter`.

    Args:
        value: The concrete choice value (free-form but JSON-safe, e.g. a
            float / string / int).  Used only for reporting.
        gain: Caller-supplied non-negative gain of this choice.  The
            hyperparameter objective maximizes the total gain of the chosen
            configuration.
        description: Free-form description.
        metadata: Free-form metadata (JSON-safe).
    """

    value: Any = None
    gain: float = 0.0
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        try:
            check_nonnegative(self.gain, label="hyperparameter choice gain")
        except MLValidationError as exc:
            raise MLValidationError(str(exc)) from exc

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "value": self.value,
            "gain": float(self.gain),
            "description": self.description,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MLHyperparameterChoice:
        """Rebuild a choice from :meth:`to_dict` output."""
        return cls(
            value=data.get("value"),
            gain=float(data.get("gain", 0.0)),
            description=str(data.get("description", "")),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class MLHyperparameter:
    """One hyperparameter with a deterministic finite choice space.

    Args:
        name: Unique hyperparameter name.
        choices: Ordered choice list (at least one).
        description: Free-form description.
        metadata: Free-form metadata (JSON-safe).
    """

    name: str
    choices: list[MLHyperparameterChoice] = field(default_factory=list)
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        try:
            check_nonempty_name(self.name, label="hyperparameter name")
        except MLValidationError as exc:
            raise MLValidationError(str(exc)) from exc
        if not self.choices:
            raise MLValidationError(f"hyperparameter {self.name!r} needs at least one choice")

    @property
    def choice_count(self) -> int:
        """Number of choices."""
        return len(self.choices)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "choices": [choice.to_dict() for choice in self.choices],
            "description": self.description,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MLHyperparameter:
        """Rebuild a hyperparameter from :meth:`to_dict` output."""
        return cls(
            name=str(data["name"]),
            choices=[MLHyperparameterChoice.from_dict(d) for d in data.get("choices", [])],
            description=str(data.get("description", "")),
            metadata=dict(data.get("metadata", {})),
        )


def _is_finite(value: float) -> bool:
    import math

    return math.isfinite(value)
