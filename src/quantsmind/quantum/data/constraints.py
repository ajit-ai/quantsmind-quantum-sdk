"""Data-domain constraints of the QMQ-09 Data Intelligence layer.

Constraints translate the domain feature-selection / clustering semantics
into QMQ-01 :class:`Constraint` instances with symbolic expressions over the
deterministic Data variable naming conventions.

Supported families:

* :class:`FeatureCountConstraint` — total number of selected features in
  ``[min_features, max_features]``,
* :class:`FeatureGroupConstraint` — per-group selection limits,
* :class:`AssignmentConstraint` — every record is assigned to exactly one
  cluster (``sum_cluster z_i_c = 1``),
* :class:`ClusterCountConstraint` — per-cluster record-count bounds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from quantsmind.quantum.data._expr import (
    cluster_variable_name,
    variable_name,
)
from quantsmind.quantum.data._validation import check_nonempty_name
from quantsmind.quantum.data.errors import DataValidationError

if TYPE_CHECKING:
    from quantsmind.quantum.core.constraint import Constraint
    from quantsmind.quantum.data.problem import DataProblem

__all__ = [
    "DataConstraint",
    "FeatureCountConstraint",
    "FeatureGroupConstraint",
    "AssignmentConstraint",
    "ClusterCountConstraint",
    "constraint_from_dict",
]


@dataclass
class DataConstraint:
    """Base class of all data constraints."""

    name: str
    description: str = ""
    kind: ClassVar[str] = "data"

    def __post_init__(self) -> None:
        try:
            check_nonempty_name(self.name, label="constraint name")
        except ValueError as exc:
            raise DataValidationError(str(exc)) from exc

    def validate(self, problem: DataProblem) -> list[str]:
        """Return deterministic validation issues for ``problem``."""
        return []

    def to_quantum_constraints(self, problem: DataProblem) -> list[Constraint]:
        """Translate into QMQ core :class:`Constraint` instances."""
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {"kind": self.kind, "name": self.name, "description": self.description}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DataConstraint:
        """Rebuild a constraint from :meth:`to_dict` output."""
        return cls(name=str(data["name"]), description=str(data.get("description", "")))


@dataclass
class FeatureCountConstraint(DataConstraint):
    """Limit the total number of selected features.

    Args:
        name: Constraint name.
        min_features: Minimum number of selected features (>= 0).
        max_features: Maximum number of selected features (``None`` = unbounded).
        description: Free-form description.
    """

    min_features: float = 1.0
    max_features: float | None = None
    kind: ClassVar[str] = "feature_count"

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.min_features is None or float(self.min_features) < 0.0:
            raise DataValidationError("min_features must be a non-negative number")
        if self.max_features is not None and float(self.max_features) < 0.0:
            raise DataValidationError("max_features must be a non-negative number")
        if self.max_features is not None and float(self.max_features) < float(self.min_features):
            raise DataValidationError("max_features cannot be below min_features")

    def validate(self, problem: DataProblem) -> list[str]:
        issues: list[str] = []
        if problem.problem_type.name != "FEATURE_SELECTION":
            issues.append("FeatureCountConstraint is only valid for feature-selection problems")
        num_features = len(problem.dataset.features)
        if num_features:
            if float(self.min_features) > num_features:
                issues.append(
                    f"min_features {self.min_features} exceeds the {num_features} dataset features"
                )
            if self.max_features is not None and float(self.max_features) > num_features:
                issues.append(
                    f"max_features {self.max_features} exceeds the {num_features} dataset features"
                )
        return issues

    def to_quantum_constraints(self, problem: DataProblem) -> list[Constraint]:
        from quantsmind.quantum.core.constraint import Constraint

        expression = (
            " + ".join(
                f"1.0*{variable_name(index)}" for index in range(len(problem.dataset.features))
            )
            or "0"
        )
        constraints: list[Constraint] = []
        if self.max_features is not None:
            constraints.append(
                Constraint.le(
                    f"{self.name}_max",
                    expression_string_for(expression),
                    float(self.max_features),
                )
            )
        constraints.append(
            Constraint.ge(
                f"{self.name}_min",
                expression_string_for(expression),
                float(self.min_features),
            )
        )
        return constraints

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "name": self.name,
            "description": self.description,
            "min_features": float(self.min_features),
            "max_features": self.max_features,
        }


@dataclass
class FeatureGroupConstraint(DataConstraint):
    """Limit the number of selected features inside one feature group.

    Args:
        name: Constraint name.
        group: Free-form group label (metadata only).
        members: Feature names of the group.
        lower: Minimum number of selected members within the group.
        upper: Maximum number of selected members within the group
            (``None`` = unbounded).
        description: Free-form description.
    """

    group: str = ""
    members: list[str] = field(default_factory=list)
    lower: float = 0.0
    upper: float | None = None
    kind: ClassVar[str] = "feature_group"

    def __post_init__(self) -> None:
        super().__post_init__()
        if float(self.lower) < 0.0:
            raise DataValidationError("group lower bound must be a non-negative number")
        if self.upper is not None and float(self.upper) < 0.0:
            raise DataValidationError("group upper bound must be a non-negative number")
        if self.upper is not None and float(self.upper) < float(self.lower):
            raise DataValidationError("group upper bound cannot be below the lower bound")
        if not self.members:
            raise DataValidationError("a feature group needs at least one member")

    def validate(self, problem: DataProblem) -> list[str]:
        issues: list[str] = []
        if problem.problem_type.name != "FEATURE_SELECTION":
            issues.append("FeatureGroupConstraint is only valid for feature-selection problems")
        unknown = sorted(set(self.members) - set(problem.dataset.feature_names))
        if unknown:
            issues.append(f"unknown features in group {self.group!r}: {unknown}")
        available = sorted(set(self.members) & set(problem.dataset.feature_names))
        if self.upper is not None and self.upper > len(available):
            issues.append(
                f"upper bound {self.upper} exceeds the {len(available)} available group features"
            )
        return issues

    def to_quantum_constraints(self, problem: DataProblem) -> list[Constraint]:
        from quantsmind.quantum.core.constraint import Constraint

        ordering = problem.dataset.feature_names
        indices = [ordering.index(name) for name in self.members]
        expression = " + ".join(f"1.0*{variable_name(index)}" for index in sorted(indices)) or "0"
        constraints: list[Constraint] = []
        if self.upper is not None:
            constraints.append(
                Constraint.le(
                    f"{self.name}_max",
                    expression_string_for(expression),
                    float(self.upper),
                )
            )
        constraints.append(
            Constraint.ge(
                f"{self.name}_min",
                expression_string_for(expression),
                float(self.lower),
            )
        )
        return constraints

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "name": self.name,
            "description": self.description,
            "group": self.group,
            "members": list(self.members),
            "lower": float(self.lower),
            "upper": self.upper,
        }


@dataclass
class AssignmentConstraint(DataConstraint):
    """Every record is assigned to exactly one cluster (``sum_c z_i_c = 1``)."""

    kind: ClassVar[str] = "assignment"

    def validate(self, problem: DataProblem) -> list[str]:
        issues: list[str] = []
        if problem.problem_type.name != "CLUSTERING":
            issues.append("AssignmentConstraint is only valid for clustering problems")
        if problem.k is None or problem.k < 1:
            issues.append("clustering requires a positive cluster count (k)")
        if not problem.dataset.records:
            issues.append("clustering requires at least one record")
        return issues

    def to_quantum_constraints(self, problem: DataProblem) -> list[Constraint]:
        from quantsmind.quantum.core.constraint import Constraint

        constraints: list[Constraint] = []
        for record_index in range(len(problem.dataset.records)):
            expression = " + ".join(
                f"1.0*{cluster_variable_name(record_index, cluster)}"
                for cluster in range(problem.k or 0)
            )
            constraints.append(
                Constraint.eq(
                    f"{self.name}_{problem.dataset.record_ids[record_index]}",
                    expression_string_for(expression),
                    1.0,
                )
            )
        return constraints


@dataclass
class ClusterCountConstraint(DataConstraint):
    """Bound the number of records assigned to every cluster.

    Args:
        name: Constraint name.
        min_records: Minimum number of records per cluster (>= 0).
        max_records: Maximum number of records per cluster (``None`` = unbounded).
        description: Free-form description.
    """

    min_records: float = 1.0
    max_records: float | None = None
    kind: ClassVar[str] = "cluster_count"

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.min_records is None or float(self.min_records) < 0.0:
            raise DataValidationError("min_records must be a non-negative number")
        if self.max_records is not None and float(self.max_records) < 0.0:
            raise DataValidationError("max_records must be a non-negative number")
        if self.max_records is not None and float(self.max_records) < float(self.min_records):
            raise DataValidationError("max_records cannot be below min_records")

    def validate(self, problem: DataProblem) -> list[str]:
        issues: list[str] = []
        if problem.problem_type.name != "CLUSTERING":
            issues.append("ClusterCountConstraint is only valid for clustering problems")
        if problem.k is None or problem.k < 1:
            issues.append("clustering requires a positive cluster count (k)")
        num_records = len(problem.dataset.records)
        if num_records:
            if float(self.min_records) > num_records:
                issues.append(
                    f"min_records {self.min_records} exceeds the {num_records} dataset records"
                )
            if self.max_records is not None and float(self.max_records) > num_records:
                issues.append(
                    f"max_records {self.max_records} exceeds the {num_records} dataset records"
                )
        return issues

    def to_quantum_constraints(self, problem: DataProblem) -> list[Constraint]:
        from quantsmind.quantum.core.constraint import Constraint

        constraints: list[Constraint] = []
        for cluster in range(problem.k or 0):
            expression = (
                " + ".join(
                    f"1.0*{cluster_variable_name(record_index, cluster)}"
                    for record_index in range(len(problem.dataset.records))
                )
                or "0"
            )
            if self.max_records is not None:
                constraints.append(
                    Constraint.le(
                        f"{self.name}_{cluster}_max",
                        expression_string_for(expression),
                        float(self.max_records),
                    )
                )
            constraints.append(
                Constraint.ge(
                    f"{self.name}_{cluster}_min",
                    expression_string_for(expression),
                    float(self.min_records),
                )
            )
        return constraints

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "name": self.name,
            "description": self.description,
            "min_records": float(self.min_records),
            "max_records": self.max_records,
        }


def constraint_from_dict(data: dict[str, Any]) -> DataConstraint:
    """Rebuild any supported Data constraint from :meth:`to_dict` output."""
    kind = str(data.get("kind", ""))
    name = str(data["name"])
    description = str(data.get("description", ""))
    if kind == "feature_count":
        return FeatureCountConstraint(
            name=name,
            description=description,
            min_features=float(data.get("min_features", 1.0)),
            max_features=(
                float(data["max_features"]) if data.get("max_features") is not None else None
            ),
        )
    if kind == "feature_group":
        return FeatureGroupConstraint(
            name=name,
            description=description,
            group=str(data.get("group", "")),
            members=[str(member) for member in data.get("members", [])],
            lower=float(data.get("lower", 0.0)),
            upper=(float(data["upper"]) if data.get("upper") is not None else None),
        )
    if kind == "assignment":
        return AssignmentConstraint(name=name, description=description)
    if kind == "cluster_count":
        return ClusterCountConstraint(
            name=name,
            description=description,
            min_records=float(data.get("min_records", 1.0)),
            max_records=(
                float(data["max_records"]) if data.get("max_records") is not None else None
            ),
        )
    raise DataValidationError(f"unknown data constraint kind {kind!r}")


def expression_string_for(expression: str) -> str:
    """Return the symbolic expression string verbatim (transparent helper)."""
    return expression
