"""Pairwise relationship matrix of the Data Intelligence layer.

:class:`DataRelationship` is a deterministic, symmetric pairwise matrix over
the ordered record identifiers (distance, similarity, adjacency or affinity).
:func:`pairwise_relationship` builds the canonical distance/similarity
relationship of a :class:`DataSet` from the Data context distance metric.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.data._validation import (
    check_nonempty_name,
    check_unique_names,
)
from quantsmind.quantum.data.errors import DataValidationError
from quantsmind.quantum.data.numerics import (
    euclidean_distance,
    squared_euclidean_distance,
    weighted_squared_euclidean_distance,
)

if TYPE_CHECKING:
    from quantsmind.quantum.data.models import DataSet

__all__ = ["DataRelationship", "RELATIONSHIP_KINDS", "pairwise_relationship"]

RELATIONSHIP_KINDS = frozenset({"distance", "similarity", "adjacency", "affinity"})

_SYMMETRY_TOLERANCE = 1e-9


@dataclass
class DataRelationship:
    """Pairwise relationship matrix over ordered record identifiers.

    Args:
        record_order: Ordered record identifiers.
        kind: One of :data:`RELATIONSHIP_KINDS`.
        values: Square symmetric matrix in ``record_order``; row/column index
            is the record index.  Mirrored for bit-for-bit symmetry.
        metadata: Free-form metadata (JSON-safe).
    """

    record_order: list[str]
    kind: str
    values: list[list[float]]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        try:
            check_nonempty_name(self.kind, label="relationship kind")
        except ValueError as exc:
            raise DataValidationError(str(exc)) from exc
        if self.kind not in RELATIONSHIP_KINDS:
            raise DataValidationError(
                f"unknown relationship kind {self.kind!r}; expected one of "
                f"{sorted(RELATIONSHIP_KINDS)}"
            )
        if not self.record_order:
            raise DataValidationError("relationship record order cannot be empty")
        check_unique_names(self.record_order, label="record")
        size = len(self.record_order)
        if len(self.values) != size:
            raise DataValidationError(
                f"relationship matrix must have {size} rows, got {len(self.values)}"
            )
        normalized: list[list[float]] = []
        for row_index, row in enumerate(self.values):
            if len(row) != size:
                raise DataValidationError(
                    f"relationship matrix row {row_index} must have {size} columns, got {len(row)}"
                )
            normalized_row: list[float] = []
            for col_index, value in enumerate(row):
                number = float(value)
                if not math.isfinite(number) or number < 0.0:
                    raise DataValidationError(
                        f"relationship matrix entry ({row_index}, {col_index}) must be "
                        f"a finite non-negative number"
                    )
                if row_index >= col_index:
                    normalized_row.append(number)
                else:
                    mirror = float(self.values[col_index][row_index])
                    if not math.isclose(number, mirror, rel_tol=0.0, abs_tol=_SYMMETRY_TOLERANCE):
                        raise DataValidationError(
                            f"relationship matrix entry ({row_index}, {col_index}) is not "
                            f"symmetrical: {number} vs {mirror}"
                        )
                    normalized_row.append((number + mirror) / 2.0)
            normalized.append(normalized_row)
        self.values = normalized

    def __len__(self) -> int:
        """Number of records."""
        return len(self.record_order)

    @property
    def size(self) -> int:
        """Number of records."""
        return len(self.record_order)

    def row(self, record_id: str) -> list[float]:
        """Return the row of ``record_id``."""
        return self.values[self.record_index(record_id)]

    def record_index(self, record_id: str) -> int:
        """Return the deterministic index of ``record_id``."""
        try:
            return self.record_order.index(record_id)
        except ValueError as exc:
            raise KeyError(f"relationship has no record {record_id!r}") from exc

    def value(self, record_a: str, record_b: str) -> float:
        """Return the pairwise value between two records."""
        return self.values[self.record_index(record_a)][self.record_index(record_b)]

    def validate_against(self, record_ids: list[str]) -> None:
        """Raise when the relationship does not cover exactly ``record_ids``."""
        if self.record_order != list(record_ids):
            raise DataValidationError(
                "relationship record order does not match the dataset record order: "
                f"{self.record_order} vs {list(record_ids)}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "record_order": list(self.record_order),
            "kind": self.kind,
            "values": [[float(value) for value in row] for row in self.values],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DataRelationship:
        """Rebuild a relationship from :meth:`to_dict` output."""
        return cls(
            record_order=[str(name) for name in data.get("record_order", [])],
            kind=str(data.get("kind", "distance")),
            values=[[float(value) for value in row] for row in data.get("values", [])],
            metadata=dict(data.get("metadata", {})),
        )


def pairwise_relationship(
    dataset: DataSet,
    *,
    kind: str = "distance",
    metric: str = "euclidean",
    weights: dict[str, float] | None = None,
) -> DataRelationship:
    """Build the deterministic pairwise relationship of ``dataset``.

    Args:
        dataset: The dataset to measure (must be structurally valid).
        kind: Relationship kind (``"distance"`` or ``"similarity"``).
        metric: One of ``"euclidean"``, ``"squared_euclidean"`` or
            ``"weighted_euclidean"`` (the latter uses ``weights`` or the
            dataset feature weights).
        weights: Optional feature name -> weight map.

    Returns:
        A symmetric :class:`DataRelationship`.
    """
    dataset.raise_if_invalid()
    if kind not in {"distance", "similarity"}:
        raise DataValidationError(
            f"pairwise builder supports kind distance/similarity, got {kind!r}"
        )
    matrix = dataset.matrix()
    feature_names = dataset.feature_names

    weight_vector: list[float] | None = None
    used_weights: dict[str, float] = {}
    if metric == "weighted_euclidean":
        source = (
            weights
            if weights is not None
            else {feature.name: feature.weight for feature in dataset.features}
        )
        used_weights = {name: float(value) for name, value in source.items()}
        unknown = sorted(set(used_weights) - set(feature_names))
        if unknown:
            raise DataValidationError(
                f"unknown weights for features {unknown} (dataset features: {feature_names})"
            )
        weight_vector = [used_weights.get(name, 0.0) for name in feature_names]

    values: list[list[float]] = []
    for left in matrix:
        row: list[float] = []
        for right in matrix:
            if metric == "euclidean":
                distance = euclidean_distance(left, right)
            elif metric == "squared_euclidean":
                distance = squared_euclidean_distance(left, right)
            else:
                assert weight_vector is not None
                distance = weighted_squared_euclidean_distance(left, right, weight_vector)
            row.append(distance if kind == "distance" else similarity_from_sigma(distance))
        values.append(row)
    return DataRelationship(
        record_order=list(dataset.record_ids),
        kind=kind,
        values=values,
        metadata={
            "metric": metric,
            "weights": used_weights,
            "dataset": dataset.name,
        },
    )


def similarity_from_sigma(distance: float) -> float:
    """Legacy-free Gaussian similarity with the default kernel width."""
    from quantsmind.quantum.data.numerics import similarity_from_distance

    return similarity_from_distance(distance, sigma=1.0)
