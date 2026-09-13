"""Data problem representation of the QMQ-09 Data Intelligence layer.

:class:`DataProblem` is the domain problem: an ordered :class:`DataSet`,
a :class:`DataProblemType`, optional objectives, optional constraints, the
Data context and the clustering hyper-parameters.  The deterministic
:meth:`DataProblem.decision_variables` mapping (feature selection ->
``x<i>``, clustering -> ``z{record}_{cluster}``) is the single contract
shared by the formulation adapter, the mapper, execution and result layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.data._expr import cluster_variable_name, variable_name
from quantsmind.quantum.data._validation import check_nonempty_name
from quantsmind.quantum.data.constraints import constraint_from_dict
from quantsmind.quantum.data.context import DataContext
from quantsmind.quantum.data.errors import DataValidationError
from quantsmind.quantum.data.models import DataSet
from quantsmind.quantum.data.objectives import objective_from_dict
from quantsmind.quantum.data.relationship import DataRelationship, pairwise_relationship

if TYPE_CHECKING:
    from quantsmind.quantum.core.variable import Variable
    from quantsmind.quantum.data.constraints import DataConstraint
    from quantsmind.quantum.data.objectives import DataObjective

__all__ = ["DataProblemType", "DataProblem"]


class DataProblemType(Enum):
    """Supported data intelligence problem families.

    Attributes:
        FEATURE_SELECTION: Binary selection of a subset of features.
        CLUSTERING: Assignment of records to ``k`` clusters.
    """

    FEATURE_SELECTION = "feature_selection"
    CLUSTERING = "clustering"

    @classmethod
    def parse(cls, value: Any) -> DataProblemType:
        """Coerce a name or member to a :class:`DataProblemType`."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower().replace("-", "_")
        for member in cls:
            if member.value == text or member.name.lower() == text:
                return member
        raise DataValidationError(
            f"unknown data problem type {value!r}; expected one of: "
            f"{', '.join(member.value for member in cls)}"
        )


@dataclass
class DataProblem:
    """Domain problem of the Data Intelligence layer.

    Args:
        name: Problem identifier.
        dataset: The ordered dataset the problem operates on.
        problem_type: Family (:attr:`DataProblemType.FEATURE_SELECTION` or
            :attr:`DataProblemType.CLUSTERING`).
        objectives: Ordered list of data objectives (names must be unique).
        constraints: Ordered list of data constraints (names must be unique).
        context: Optional Data context (distance metric / strategy intent).
        k: Number of clusters (clustering problems only).
        pairwise: Optional precomputed pairwise relationship (clustering
            only; recomputed deterministically when ``None``).
        description: Free-form description.
        metadata: Free-form metadata (JSON-safe).

    Raises:
        DataValidationError: On duplicate objective/constraint names,
            invalid problem-type hyper-parameters or a clustering/feature
            selection configuration mix-up.
    """

    name: str
    dataset: DataSet
    problem_type: DataProblemType = DataProblemType.FEATURE_SELECTION
    objectives: list[DataObjective] = field(default_factory=list)
    constraints: list[DataConstraint] = field(default_factory=list)
    context: DataContext | None = None
    k: int | None = None
    pairwise: DataRelationship | None = None
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        try:
            check_nonempty_name(self.name, label="data problem name")
        except ValueError as exc:
            raise DataValidationError(str(exc)) from exc
        self.problem_type = DataProblemType.parse(self.problem_type)
        self._check_unique_names()
        if self.problem_type is DataProblemType.CLUSTERING:
            if self.k is None or int(self.k) < 1:
                raise DataValidationError(
                    "clustering problems require a positive cluster count (k)"
                )
            if int(self.k) > len(self.dataset.records):
                raise DataValidationError(
                    f"cluster count k={self.k} exceeds the {len(self.dataset.records)} records"
                )
        else:
            if self.k is not None:
                raise DataValidationError("k is only valid for clustering problems")
            if self.pairwise is not None:
                raise DataValidationError(
                    "pairwise relationships are only valid for clustering problems"
                )

    @property
    def num_features(self) -> int:
        """Number of features of the underlying dataset."""
        return len(self.dataset.features)

    @property
    def num_records(self) -> int:
        """Number of records of the underlying dataset."""
        return len(self.dataset.records)

    @property
    def size(self) -> int:
        """Number of decision variables."""
        if self.problem_type is DataProblemType.CLUSTERING:
            return self.num_records * (self.k or 0)
        return self.num_features

    def _check_unique_names(self) -> None:
        objective_names = [objective.name for objective in self.objectives]
        constraint_names = [constraint.name for constraint in self.constraints]
        if len(set(objective_names)) != len(objective_names):
            raise DataValidationError("data problem objective names must be unique")
        if len(set(constraint_names)) != len(constraint_names):
            raise DataValidationError("data problem constraint names must be unique")

    def feature_variables(self) -> list[Variable]:
        """Return the binary feature variables ``x0 .. x{n-1}`` in feature order."""
        from quantsmind.quantum.core.variable import Variable

        return [
            Variable.binary(
                name=variable_name(index),
                domain="data.feature",
                description=f"selection of feature {feature.name!r}",
            )
            for index, feature in enumerate(self.dataset.features)
        ]

    def cluster_variables(self) -> list[Variable]:
        """Return the binary assignment variables in record-major order."""
        from quantsmind.quantum.core.variable import Variable

        variables: list[Variable] = []
        for record_index, record in enumerate(self.dataset.records):
            for cluster in range(self.k or 0):
                variables.append(
                    Variable.binary(
                        name=cluster_variable_name(record_index, cluster),
                        domain="data.cluster",
                        description=(
                            f"assignment of record {record.record_id!r} to cluster {cluster}"
                        ),
                    )
                )
        return variables

    def decision_variables(self) -> list[Variable]:
        """Return the deterministic decision-variable list for this problem.

        Feature selection yields one binary variable per feature in dataset
        order.  Clustering yields one binary variable per (record, cluster)
        pair in record-major order so that ``record = z` record index``
        blocks are contiguous.
        """
        if self.problem_type is DataProblemType.FEATURE_SELECTION:
            if not self.dataset.features:
                raise DataValidationError(
                    "cannot build feature-selection variables without dataset features"
                )
            return self.feature_variables()
        if not self.dataset.records:
            raise DataValidationError("cannot build clustering variables without dataset records")
        return self.cluster_variables()

    def clustering_distance_matrix(self) -> DataRelationship:
        """Return the pairwise distance relationship used by clustering.

        Uses :attr:`pairwise` when supplied (after validating the record
        alignment) and otherwise recomputes the deterministic
        ``distance`` relationship from the Data context distance metric.
        """
        if self.problem_type is not DataProblemType.CLUSTERING:
            raise DataValidationError(
                "clustering distance matrix is only defined for clustering problems"
            )
        if self.pairwise is not None:
            self.pairwise.validate_against(self.dataset.record_ids)
            return self.pairwise
        metric = self.context.distance_metric if self.context is not None else "euclidean"
        weights = self.context.feature_weights if self.context is not None else None
        return pairwise_relationship(
            self.dataset,
            kind="distance",
            metric=metric,
            weights=weights,
        )

    def validate(self) -> list[str]:
        """Return deterministic validation issues (never raises)."""
        issues: list[str] = []
        try:
            self.dataset.raise_if_invalid()
        except DataValidationError as exc:
            issues.append(str(exc))
        if not self.objectives:
            issues.append("data problem has no objectives")
        if self.problem_type is DataProblemType.FEATURE_SELECTION:
            if not self.dataset.features:
                issues.append("feature selection requires at least one feature")
        else:
            if not self.dataset.records:
                issues.append("clustering requires at least one record")
            if self.pairwise is not None:
                try:
                    self.pairwise.validate_against(self.dataset.record_ids)
                except DataValidationError as exc:
                    issues.append(str(exc))
        for objective in self.objectives:
            issues.extend(objective.validate(self))
        for constraint in self.constraints:
            issues.extend(constraint.validate(self))
        return sorted(set(issue for issue in issues if issue))

    def raise_if_invalid(self) -> None:
        """Raise :class:`DataValidationError` with all validation issues."""
        issues = self.validate()
        if issues:
            raise DataValidationError(f"invalid data problem {self.name!r}: " + "; ".join(issues))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "dataset": self.dataset.to_dict(),
            "problem_type": self.problem_type.value,
            "objectives": [objective.to_dict() for objective in self.objectives],
            "constraints": [constraint.to_dict() for constraint in self.constraints],
            "context": self.context.to_dict() if self.context is not None else None,
            "k": int(self.k) if self.k is not None else None,
            "pairwise": self.pairwise.to_dict() if self.pairwise is not None else None,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DataProblem:
        """Rebuild a problem from :meth:`to_dict` output."""
        pairwise_data = data.get("pairwise")
        return cls(
            name=str(data["name"]),
            description=str(data.get("description", "")),
            dataset=DataSet.from_dict(dict(data["dataset"])),
            problem_type=DataProblemType.parse(data.get("problem_type", "feature_selection")),
            objectives=[objective_from_dict(d) for d in data.get("objectives", [])],
            constraints=[constraint_from_dict(d) for d in data.get("constraints", [])],
            context=(
                DataContext.from_dict(dict(data["context"]))
                if data.get("context") is not None
                else None
            ),
            k=int(data["k"]) if data.get("k") is not None else None,
            pairwise=(
                DataRelationship.from_dict(dict(pairwise_data))
                if pairwise_data is not None
                else None
            ),
            metadata=dict(data.get("metadata", {})),
        )
