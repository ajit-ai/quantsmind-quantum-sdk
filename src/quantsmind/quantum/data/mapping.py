"""QMQ-09 data-domain mappings.

The mapper translates the domain Data variable naming conventions
(``x<i>`` for feature selection, ``z{record}_{cluster}`` for clustering)
into a deterministic :class:`DataMapping` that decodes QMQ assignments back
into domain-readable decisions (selected features and cluster assignments).

The mapper handles:

* ``x<i>`` feature-selection variables (binary, ``[0, 1]``),
* ``z{record}_{cluster}`` clustering assignment variables (binary,
  record-major),
* automatic slack-value tolerance when decoding (``selected_threshold``
  applies to binary feature variables; cluster variables use a ``>= 0.5``
  rule),
* deterministic ordering and index mapping.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from quantsmind.quantum.data._expr import (
    cluster_variable_name,
    variable_name,
)
from quantsmind.quantum.data.problem import DataProblem, DataProblemType

__all__ = [
    "DecodedDataFeature",
    "DecodedClusterAssignment",
    "DataMapping",
    "DataMapper",
]


@dataclass
class DecodedDataFeature:
    """One decoded feature-selection decision.

    Attributes:
        feature_name: Domain feature name.
        index: Deterministic feature index.
        variable_name: QMQ variable name (``x<i>``).
        value: Raw assignment value (0.0 or 1.0).
        selected: Whether the value exceeds the selection threshold.
    """

    feature_name: str
    index: int
    variable_name: str
    value: float
    selected: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_name": self.feature_name,
            "index": self.index,
            "variable_name": self.variable_name,
            "value": float(self.value),
            "selected": bool(self.selected),
        }


@dataclass
class DecodedClusterAssignment:
    """One decoded cluster assignment decision.

    Attributes:
        record_id: Domain record identifier.
        record_index: Deterministic record index.
        cluster_index: Deterministic cluster index.
        variable_name: QMQ variable name (``z{record}_{cluster}``).
        value: Raw assignment value (0.0 or 1.0).
    """

    record_id: str
    record_index: int
    cluster_index: int
    variable_name: str
    value: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "record_index": self.record_index,
            "cluster_index": self.cluster_index,
            "variable_name": self.variable_name,
            "value": float(self.value),
        }


@dataclass
class DataMapping:
    """Deterministic mapping between Data variables and QMQ indices.

    Created by :meth:`DataMapper.map` from a validated
    :class:`DataProblem`.
    """

    problem_name: str
    problem_type: DataProblemType
    feature_order: list[str]
    record_order: list[str]
    k: int | None = None

    def __post_init__(self) -> None:
        self.problem_type = DataProblemType.parse(self.problem_type)

    @property
    def variable_names(self) -> list[str]:
        """QMQ variable names in deterministic order."""
        if self.problem_type is DataProblemType.FEATURE_SELECTION:
            return [variable_name(index) for index in range(len(self.feature_order))]
        return [
            cluster_variable_name(record_index, cluster)
            for record_index in range(len(self.record_order))
            for cluster in range(self.k or 0)
        ]

    def feature_variable(self, feature_name: str) -> str:
        """Return the QMQ variable name for ``feature_name``."""
        return variable_name(self.feature_index(feature_name))

    def feature_index(self, feature_name: str) -> int:
        """Return the deterministic index of ``feature_name``."""
        try:
            return self.feature_order.index(feature_name)
        except ValueError as exc:
            raise KeyError(f"feature {feature_name!r} not in problem feature order") from exc

    def feature(self, variable_name: str) -> DecodedDataFeature | None:
        """Return the decoded feature for ``variable_name`` (or ``None``)."""
        try:
            index = int(variable_name.removeprefix("x"))
            if variable_name.startswith("x") and 0 <= index < len(self.feature_order):
                name = self.feature_order[index]
                return DecodedDataFeature(
                    feature_name=name,
                    index=index,
                    variable_name=variable_name,
                    value=0.0,
                    selected=False,
                )
        except (ValueError, IndexError):
            return None
        return None

    def cluster_variable(self, record_id: str, cluster_index: int) -> str:
        """Return the QMQ variable name for ``record_id`` and ``cluster_index``."""
        try:
            record_index = self.record_order.index(record_id)
        except ValueError as exc:
            raise KeyError(f"record {record_id!r} not in problem record order") from exc
        return cluster_variable_name(record_index, cluster_index)

    def cluster(self, record_index: int, cluster_index: int) -> DecodedClusterAssignment | None:
        """Return the decoded cluster assignment for the variable at the given indices."""
        if record_index < 0 or record_index >= len(self.record_order):
            return None
        if self.k is None or cluster_index < 0 or cluster_index >= int(self.k):
            return None
        name = cluster_variable_name(record_index, cluster_index)
        return DecodedClusterAssignment(
            record_id=self.record_order[record_index],
            record_index=record_index,
            cluster_index=cluster_index,
            variable_name=name,
            value=0.0,
        )

    def cluster_of(self, assignments: dict[str, float], record_id: str) -> int | None:
        """Return the cluster assigned to ``record_id`` (or ``None``)."""
        try:
            record_index = self.record_order.index(record_id)
        except ValueError as exc:
            raise KeyError(f"record {record_id!r} not in problem record order") from exc
        for cluster in range(self.k or 0):
            name = cluster_variable_name(record_index, cluster)
            value = float(assignments.get(name, 0.0))
            if value >= 0.5:
                return cluster
        return None

    def decode_assignments(
        self,
        assignments: dict[str, float],
        *,
        selected_threshold: float = 0.5,
    ) -> list[DecodedDataFeature] | list[DecodedClusterAssignment]:
        """Decode raw QMQ assignments into domain-readable decisions."""
        if self.problem_type is DataProblemType.FEATURE_SELECTION:
            return self._decode_features(assignments, selected_threshold=selected_threshold)
        return self._decode_clusters(assignments)

    def _decode_features(
        self,
        assignments: dict[str, float],
        *,
        selected_threshold: float,
    ) -> list[DecodedDataFeature]:
        decoded: list[DecodedDataFeature] = []
        for index, name in enumerate(self.feature_order):
            var = variable_name(index)
            value = float(assignments.get(var, 0.0))
            decoded.append(
                DecodedDataFeature(
                    feature_name=name,
                    index=index,
                    variable_name=var,
                    value=value,
                    selected=value >= selected_threshold,
                )
            )
        return decoded

    def _decode_clusters(
        self,
        assignments: dict[str, float],
    ) -> list[DecodedClusterAssignment]:
        decoded: list[DecodedClusterAssignment] = []
        for record_index, record_id in enumerate(self.record_order):
            for cluster in range(self.k or 0):
                name = cluster_variable_name(record_index, cluster)
                value = float(assignments.get(name, 0.0))
                decoded.append(
                    DecodedClusterAssignment(
                        record_id=record_id,
                        record_index=record_index,
                        cluster_index=cluster,
                        variable_name=name,
                        value=value,
                    )
                )
        return decoded


@dataclass
class DataMapper:
    """Maps a validated Data problem to a deterministic variable mapping.

    Mirrors the :class:`FinanceAssetMapper` pattern: validates, then
    provides :meth:`map` (which returns a :class:`DataMapping`) and
    :meth:`decode_assignments` (which directly returns decoded decisions).
    """

    def map(self, problem: DataProblem) -> DataMapping:
        """Return the deterministic variable mapping of ``problem``."""
        problem.raise_if_invalid()
        return DataMapping(
            problem_name=problem.name,
            problem_type=problem.problem_type,
            feature_order=list(problem.dataset.feature_names),
            record_order=list(problem.dataset.record_ids),
            k=int(problem.k) if problem.k is not None else None,
        )

    def decode_assignments(
        self,
        problem: DataProblem,
        assignments: dict[str, float],
        *,
        selected_threshold: float = 0.5,
    ) -> list[DecodedDataFeature] | list[DecodedClusterAssignment]:
        """Decode raw QMQ assignments into domain-readable decisions."""
        return self.map(problem).decode_assignments(
            assignments, selected_threshold=selected_threshold
        )
