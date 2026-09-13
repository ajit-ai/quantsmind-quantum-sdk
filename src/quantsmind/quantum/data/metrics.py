"""Data-metrics computation of the QMQ-09 Data Intelligence layer.

:class:`DataMetrics` summarises the domain outcome of a Data solve: selected
features and their utility/cost, cluster structure and the total
within-cluster distance, plus the existing QMQ-05 constraint-violation
counts.  Computations are deterministic and reuse the QMQ-05
:func:`constraint_violations` helper (never recomputed ad hoc).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from quantsmind.quantum.data.mapping import (
    DataMapper,
    DecodedDataFeature,
)
from quantsmind.quantum.data.objectives import (
    FeatureSelectionObjective,
    FeatureUtilityObjective,
    SelectionCostObjective,
)
from quantsmind.quantum.data.problem import DataProblem, DataProblemType

__all__ = ["DataMetrics"]


@dataclass
class DataMetrics:
    """Deterministic outcome metrics of a Data solve.

    Attributes:
        problem_type: Data problem family (``"feature_selection"`` or
            ``"clustering"``).
        selected_feature_count: Number of selected features (FS).
        selected_utility: Total utility of the selected features (FS).
        selection_cost: Total cost of the selected features (FS).
        net_objective: Primary objective value (``utility - penalty*cost``
            for FS, total within-cluster distance for clustering).
        cluster_count: Number of non-empty clusters (clustering).
        total_within_cluster_distance: Total within-cluster pairwise
            distance (clustering).
        constraint_violations: Number of violated QMQ constraints.
        constraint_violation_magnitude: Aggregate violation magnitude.
        metadata: Free-form metadata (JSON-safe).
    """

    problem_type: str = ""
    selected_feature_count: int = 0
    selected_utility: float = 0.0
    selection_cost: float = 0.0
    net_objective: float = 0.0
    cluster_count: int = 0
    total_within_cluster_distance: float | None = None
    constraint_violations: int = 0
    constraint_violation_magnitude: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def compute(
        cls,
        problem: DataProblem,
        assignments: dict[str, float],
        *,
        selected_threshold: float = 0.5,
        violation_count: int = 0,
        violation_magnitude: float = 0.0,
    ) -> DataMetrics:
        """Compute deterministic metrics from raw QMQ assignments."""
        decoded = (
            DataMapper()
            .map(problem)
            .decode_assignments(assignments, selected_threshold=selected_threshold)
        )
        if problem.problem_type is DataProblemType.FEATURE_SELECTION:
            features = [item for item in decoded if isinstance(item, DecodedDataFeature)]
            selected = [item.feature_name for item in features if item.selected]
            selected_utility = sum(cls._utility(problem, name) for name in selected)
            selection_cost = sum(cls._cost(problem, name) for name in selected)
            penalty_weight = sum(
                objective.penalty
                for objective in problem.objectives
                if isinstance(objective, FeatureSelectionObjective)
            )
            return cls(
                problem_type=problem.problem_type.value,
                selected_feature_count=len(selected),
                selected_utility=selected_utility,
                selection_cost=selection_cost,
                net_objective=selected_utility - penalty_weight * selection_cost,
                constraint_violations=int(violation_count),
                constraint_violation_magnitude=float(violation_magnitude),
            )

        used_clusters: set[int] = set()
        assignments_by_record: dict[str, int] = {}
        for record_id in problem.dataset.record_ids:
            cluster = DataMapper().map(problem).cluster_of(assignments, record_id)
            if cluster is not None:
                used_clusters.add(cluster)
                assignments_by_record[record_id] = cluster
        cluster_count = len(used_clusters)

        distances = problem.clustering_distance_matrix()
        total: float = 0.0
        records = problem.dataset.record_ids
        for i in range(len(records)):
            for j in range(i + 1, len(records)):
                first = records[i]
                second = records[j]
                if (
                    first in assignments_by_record
                    and second in assignments_by_record
                    and assignments_by_record[first] == assignments_by_record[second]
                ):
                    total += float(distances.values[i][j])
        return cls(
            problem_type=problem.problem_type.value,
            cluster_count=cluster_count,
            total_within_cluster_distance=total,
            net_objective=total,
            constraint_violations=int(violation_count),
            constraint_violation_magnitude=float(violation_magnitude),
        )

    @staticmethod
    def _utility(problem: DataProblem, feature_name: str) -> float:
        total = 0.0
        for objective in problem.objectives:
            kinds = (FeatureUtilityObjective, FeatureSelectionObjective)
            if isinstance(objective, kinds):
                total += objective.utilities.get(feature_name, 0.0)
        return total

    @staticmethod
    def _cost(problem: DataProblem, feature_name: str) -> float:
        total = 0.0
        for objective in problem.objectives:
            kinds = (SelectionCostObjective, FeatureSelectionObjective)
            if isinstance(objective, kinds):
                total += objective.costs.get(feature_name, 0.0)
        return total

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "problem_type": self.problem_type,
            "selected_feature_count": int(self.selected_feature_count),
            "selected_utility": float(self.selected_utility),
            "selection_cost": float(self.selection_cost),
            "net_objective": float(self.net_objective),
            "cluster_count": int(self.cluster_count),
            "total_within_cluster_distance": self.total_within_cluster_distance,
            "constraint_violations": int(self.constraint_violations),
            "constraint_violation_magnitude": float(self.constraint_violation_magnitude),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DataMetrics:
        """Rebuild metrics from :meth:`to_dict` output."""
        within = data.get("total_within_cluster_distance")
        return cls(
            problem_type=str(data.get("problem_type", "")),
            selected_feature_count=int(data.get("selected_feature_count", 0)),
            selected_utility=float(data.get("selected_utility", 0.0)),
            selection_cost=float(data.get("selection_cost", 0.0)),
            net_objective=float(data.get("net_objective", 0.0)),
            cluster_count=int(data.get("cluster_count", 0)),
            total_within_cluster_distance=(float(within) if within is not None else None),
            constraint_violations=int(data.get("constraint_violations", 0)),
            constraint_violation_magnitude=float(data.get("constraint_violation_magnitude", 0.0)),
            metadata=dict(data.get("metadata", {})),
        )
