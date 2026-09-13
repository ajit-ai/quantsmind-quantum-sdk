"""ML-domain constraints of the QMQ-10 AI/ML Intelligence layer.

Constraints translate the domain fitting, model-selection and
hyperparameter-selection semantics into QMQ-01 :class:`Constraint` instances
with symbolic expressions over the deterministic ML variable naming
conventions.

Supported families:

* :class:`MLCoefficientCountConstraint` — bound the number of non-zero
  fitting coefficients (classification / regression),
* :class:`ModelSelectionOneHotConstraint` — exactly one candidate is
  selected (equality sum = 1),
* :class:`HyperparameterOnePerParameterConstraint` — exactly one choice is
  selected per hyperparameter,
* :class:`MLFeatureCountConstraint` — bound the number of selected features
  (delegated to QMQ-09 Data layer),
* :class:`MLAssignmentConstraint` — every record is assigned to exactly one
  cluster (delegated to QMQ-09 Data layer),
* :class:`MLClusterCountConstraint` — bound per-cluster record counts
  (delegated to QMQ-09 Data layer).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

from quantsmind.quantum.ml._expr import (
    coefficient_variable_names,
    hyperparameter_variable_name,
    linear_string,
    selection_variable_names,
)
from quantsmind.quantum.ml._validation import check_nonempty_name
from quantsmind.quantum.ml.errors import MLValidationError

if TYPE_CHECKING:
    from quantsmind.quantum.core.constraint import Constraint
    from quantsmind.quantum.ml.problem import MLProblem

__all__ = [
    "MLConstraint",
    "MLCoefficientCountConstraint",
    "ModelSelectionOneHotConstraint",
    "HyperparameterOnePerParameterConstraint",
    "MLFeatureCountConstraint",
    "MLAssignmentConstraint",
    "MLClusterCountConstraint",
    "constraint_from_dict",
]


@dataclass
class MLConstraint:
    """Base class of all ML constraints."""

    name: str
    description: str = ""
    kind: ClassVar[str] = "ml"

    def __post_init__(self) -> None:
        try:
            check_nonempty_name(self.name, label="constraint name")
        except MLValidationError as exc:
            raise MLValidationError(str(exc)) from exc

    def validate(self, problem: MLProblem) -> list[str]:
        """Return deterministic validation issues for ``problem``."""
        return []

    def to_quantum_constraints(self, problem: MLProblem) -> list[Constraint]:
        """Translate into QMQ core :class:`Constraint` instances."""
        raise NotImplementedError

    def to_data_constraint(self, problem: MLProblem | None = None) -> Any:
        """Translate into a QMQ-09 data constraint (delegated constraints only)."""
        raise MLValidationError(f"constraint {self.kind!r} is not delegated to the data layer")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {"kind": self.kind, "name": self.name, "description": self.description}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MLConstraint:
        """Rebuild a constraint from :meth:`to_dict` output."""
        return cls(name=str(data["name"]), description=str(data.get("description", "")))

    @property
    def domain(self) -> str:
        """ML-domain label of this constraint."""
        return f"ml/{self.kind}"


@dataclass
class MLCoefficientCountConstraint(MLConstraint):
    """Bound the total number of selected fitting coefficients.

    Args:
        name: Constraint name.
        min_coefficients: Minimum number of non-zero coefficients (>= 0).
        max_coefficients: Maximum number of non-zero coefficients
            (``None`` = unbounded).
        description: Free-form description.
    """

    min_coefficients: float = 1.0
    max_coefficients: float | None = None
    kind: ClassVar[str] = "ml_coefficient_count"

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.min_coefficients is None or float(self.min_coefficients) < 0.0:
            raise MLValidationError("min_coefficients must be a non-negative number")
        if self.max_coefficients is not None and float(self.max_coefficients) < 0.0:
            raise MLValidationError("max_coefficients must be a non-negative number")
        if self.max_coefficients is not None and float(self.max_coefficients) < float(
            self.min_coefficients
        ):
            raise MLValidationError("max_coefficients cannot be below min_coefficients")

    def validate(self, problem: MLProblem) -> list[str]:
        issues: list[str] = []
        if problem.problem_type.name not in ("CLASSIFICATION", "REGRESSION"):
            issues.append(
                "MLCoefficientCountConstraint is only valid for classification/regression"
            )
        if problem.dataset is not None:
            num_features = len(problem.dataset.features)
            if num_features:
                if float(self.min_coefficients) > num_features:
                    issues.append(
                        f"min_coefficients {self.min_coefficients} exceeds the "
                        f"{num_features} dataset features"
                    )
                if (
                    self.max_coefficients is not None
                    and float(self.max_coefficients) > num_features
                ):
                    issues.append(
                        f"max_coefficients {self.max_coefficients} exceeds the "
                        f"{num_features} dataset features"
                    )
        return issues

    def to_quantum_constraints(self, problem: MLProblem) -> list[Constraint]:
        from quantsmind.quantum.core.constraint import Constraint

        num_features = len(problem.dataset.features) if problem.dataset is not None else 0
        var_names = coefficient_variable_names(num_features)
        coefficients = [1.0] * num_features
        expression = linear_string(coefficients, var_names) if var_names else "0"
        constraints: list[Constraint] = []
        if self.max_coefficients is not None:
            constraints.append(
                Constraint.le(
                    f"{self.name}_max",
                    expression,
                    float(self.max_coefficients),
                )
            )
        constraints.append(
            Constraint.ge(
                f"{self.name}_min",
                expression,
                float(self.min_coefficients),
            )
        )
        return constraints

    def to_dict(self) -> dict[str, Any]:
        return {
            **super().to_dict(),
            "min_coefficients": float(self.min_coefficients),
            "max_coefficients": self.max_coefficients,
        }


@dataclass
class ModelSelectionOneHotConstraint(MLConstraint):
    """Exactly one candidate is selected (``sum_c s_c = 1``)."""

    kind: ClassVar[str] = "model_selection_one_hot"

    def validate(self, problem: MLProblem) -> list[str]:
        issues: list[str] = []
        if problem.problem_type.name != "MODEL_SELECTION":
            issues.append("ModelSelectionOneHotConstraint is only valid for model-selection")
        if not problem.candidates:
            issues.append("model selection requires at least one candidate")
        return issues

    def to_quantum_constraints(self, problem: MLProblem) -> list[Constraint]:
        from quantsmind.quantum.core.constraint import Constraint

        var_names = selection_variable_names(len(problem.candidates))
        coefficients = [1.0] * len(var_names)
        expression = linear_string(coefficients, var_names) if var_names else "0"
        return [Constraint.eq(f"{self.name}_onehot", expression, 1.0)]


@dataclass
class HyperparameterOnePerParameterConstraint(MLConstraint):
    """Exactly one choice per hyperparameter (``sum_c h_{p,c} = 1`` per p)."""

    kind: ClassVar[str] = "hyperparameter_one_per_parameter"

    def validate(self, problem: MLProblem) -> list[str]:
        issues: list[str] = []
        if problem.problem_type.name != "HYPERPARAMETER_OPTIMIZATION":
            issues.append(
                "HyperparameterOnePerParameterConstraint is only valid for hyperparameter problems"
            )
        if not problem.hyperparameters:
            issues.append("hyperparameter optimization requires at least one hyperparameter")
        return issues

    def to_quantum_constraints(self, problem: MLProblem) -> list[Constraint]:
        from quantsmind.quantum.core.constraint import Constraint

        constraints: list[Constraint] = []
        for param_index, hyperparameter in enumerate(problem.hyperparameters):
            var_names = [
                hyperparameter_variable_name(param_index, ci)
                for ci in range(hyperparameter.choice_count)
            ]
            coefficients = [1.0] * len(var_names)
            expression = linear_string(coefficients, var_names) if var_names else "0"
            constraints.append(
                Constraint.eq(
                    f"{self.name}_{hyperparameter.name}",
                    expression,
                    1.0,
                )
            )
        return constraints


@dataclass
class MLFeatureCountConstraint(MLConstraint):
    """Bound the number of selected features (delegated to QMQ-09).

    Converted into a Data ``FeatureCountConstraint`` at formulation time.
    """

    min_features: float = 1.0
    max_features: float | None = None
    kind: ClassVar[str] = "ml_feature_count"

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.min_features is None or float(self.min_features) < 0.0:
            raise MLValidationError("min_features must be a non-negative number")
        if self.max_features is not None and float(self.max_features) < 0.0:
            raise MLValidationError("max_features must be a non-negative number")
        if self.max_features is not None and float(self.max_features) < float(self.min_features):
            raise MLValidationError("max_features cannot be below min_features")

    def validate(self, problem: MLProblem) -> list[str]:
        issues: list[str] = []
        if problem.problem_type.name != "FEATURE_SELECTION":
            issues.append("MLFeatureCountConstraint is only valid for feature-selection")
        if problem.dataset is not None:
            num_features = len(problem.dataset.features)
            if num_features:
                if float(self.min_features) > num_features:
                    issues.append(
                        f"min_features {self.min_features} exceeds the {num_features} features"
                    )
                if self.max_features is not None and float(self.max_features) > num_features:
                    issues.append(
                        f"max_features {self.max_features} exceeds the {num_features} features"
                    )
        return issues

    def to_quantum_constraints(self, problem: MLProblem) -> list[Constraint]:
        raise NotImplementedError("MLFeatureCountConstraint is delegated to the QMQ-09 Data layer")

    def to_data_constraint(self, problem: MLProblem | None = None) -> Any:
        """Return the equivalent QMQ-09 Data constraint."""
        from quantsmind.quantum.data.constraints import FeatureCountConstraint

        return FeatureCountConstraint(
            name=self.name,
            description=self.description,
            min_features=float(self.min_features),
            max_features=(float(self.max_features) if self.max_features is not None else None),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            **super().to_dict(),
            "min_features": float(self.min_features),
            "max_features": self.max_features,
        }


@dataclass
class MLAssignmentConstraint(MLConstraint):
    """Delegated: every record assigned to exactly one cluster."""

    kind: ClassVar[str] = "ml_assignment"

    def validate(self, problem: MLProblem) -> list[str]:
        issues: list[str] = []
        if problem.problem_type.name != "CLUSTERING":
            issues.append("MLAssignmentConstraint is only valid for clustering")
        return issues

    def to_quantum_constraints(self, problem: MLProblem) -> list[Constraint]:
        raise NotImplementedError("MLAssignmentConstraint is delegated to the QMQ-09 Data layer")

    def to_data_constraint(self, problem: MLProblem | None = None) -> Any:
        """Return the equivalent QMQ-09 Data constraint."""
        from quantsmind.quantum.data.constraints import AssignmentConstraint

        return AssignmentConstraint(name=self.name, description=self.description)


@dataclass
class MLClusterCountConstraint(MLConstraint):
    """Delegated: bound per-cluster record counts."""

    min_records: float = 1.0
    max_records: float | None = None
    kind: ClassVar[str] = "ml_cluster_count"

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.min_records is None or float(self.min_records) < 0.0:
            raise MLValidationError("min_records must be a non-negative number")
        if self.max_records is not None and float(self.max_records) < 0.0:
            raise MLValidationError("max_records must be a non-negative number")
        if self.max_records is not None and float(self.max_records) < float(self.min_records):
            raise MLValidationError("max_records cannot be below min_records")

    def validate(self, problem: MLProblem) -> list[str]:
        issues: list[str] = []
        if problem.problem_type.name != "CLUSTERING":
            issues.append("MLClusterCountConstraint is only valid for clustering")
        return issues

    def to_quantum_constraints(self, problem: MLProblem) -> list[Constraint]:
        raise NotImplementedError("MLClusterCountConstraint is delegated to the QMQ-09 Data layer")

    def to_data_constraint(self, problem: MLProblem | None = None) -> Any:
        """Return the equivalent QMQ-09 Data constraint."""
        from quantsmind.quantum.data.constraints import ClusterCountConstraint

        return ClusterCountConstraint(
            name=self.name,
            description=self.description,
            min_records=float(self.min_records),
            max_records=(float(self.max_records) if self.max_records is not None else None),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            **super().to_dict(),
            "min_records": float(self.min_records),
            "max_records": self.max_records,
        }


def constraint_from_dict(data: dict[str, Any]) -> MLConstraint:
    """Rebuild any supported ML constraint from :meth:`to_dict` output."""
    kind = str(data.get("kind", ""))
    name = str(data["name"])
    description = str(data.get("description", ""))
    if kind == "ml_coefficient_count":
        return MLCoefficientCountConstraint(
            name=name,
            description=description,
            min_coefficients=float(data.get("min_coefficients", 1.0)),
            max_coefficients=(
                float(data["max_coefficients"])
                if data.get("max_coefficients") is not None
                else None
            ),
        )
    if kind == "model_selection_one_hot":
        return ModelSelectionOneHotConstraint(name=name, description=description)
    if kind == "hyperparameter_one_per_parameter":
        return HyperparameterOnePerParameterConstraint(name=name, description=description)
    if kind == "ml_feature_count":
        return MLFeatureCountConstraint(
            name=name,
            description=description,
            min_features=float(data.get("min_features", 1.0)),
            max_features=(
                float(data["max_features"]) if data.get("max_features") is not None else None
            ),
        )
    if kind == "ml_assignment":
        return MLAssignmentConstraint(name=name, description=description)
    if kind == "ml_cluster_count":
        return MLClusterCountConstraint(
            name=name,
            description=description,
            min_records=float(data.get("min_records", 1.0)),
            max_records=(
                float(data["max_records"]) if data.get("max_records") is not None else None
            ),
        )
    raise MLValidationError(f"unknown ML constraint kind {kind!r}")
