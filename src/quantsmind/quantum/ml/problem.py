"""ML problem representation of the QMQ-10 AI/ML Intelligence layer.

:class:`MLProblem` is the domain problem: an ordered :class:`MLDataSet`
(fitting / feature selection / clustering families), optional objectives,
optional constraints, the ML context, the model-selection candidates, the
hyperparameter space and the clustering ``k``.  The deterministic
:meth:`MLProblem.decision_variables` mapping (coefficients -> ``w<i>``,
model selection -> ``s<c>``, hyperparameters -> ``h{p}_{c}``) is the single
contract shared by the formulation adapter, the mapper, execution and result
layers.  Feature selection and clustering are delegated to the QMQ-09 Data
layer through a ``DataProblem`` built from the same dataset.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from quantsmind.quantum.ml._expr import (
    coefficient_variable_name,
    hyperparameter_variable_name,
    selection_variable_name,
)
from quantsmind.quantum.ml._validation import check_nonempty_name
from quantsmind.quantum.ml.constraints import (
    MLConstraint,
    constraint_from_dict,
)
from quantsmind.quantum.ml.context import MLContext
from quantsmind.quantum.ml.errors import MLValidationError
from quantsmind.quantum.ml.models import (
    MLDataSet,
    MLHyperparameter,
    MLModelCandidate,
)
from quantsmind.quantum.ml.objectives import MLObjective, objective_from_dict

if TYPE_CHECKING:
    from quantsmind.quantum.core.variable import Variable

__all__ = ["MLProblemType", "MLProblem"]

_FITTING_TYPES = frozenset({"CLASSIFICATION", "REGRESSION"})
_DELEGATED_TYPES = frozenset({"FEATURE_SELECTION", "CLUSTERING"})

_ALLOWED_OBJECTIVE_KINDS: dict[str, frozenset[str]] = {
    "CLASSIFICATION": frozenset({"classification_loss"}),
    "REGRESSION": frozenset({"regression_loss"}),
    "FEATURE_SELECTION": frozenset({"ml_feature_selection"}),
    "MODEL_SELECTION": frozenset({"model_selection"}),
    "HYPERPARAMETER_OPTIMIZATION": frozenset({"hyperparameter"}),
    "CLUSTERING": frozenset({"ml_clustering_distance"}),
}

_ALLOWED_CONSTRAINT_KINDS: dict[str, frozenset[str]] = {
    "CLASSIFICATION": frozenset({"ml_coefficient_count"}),
    "REGRESSION": frozenset({"ml_coefficient_count"}),
    "FEATURE_SELECTION": frozenset({"ml_feature_count"}),
    "MODEL_SELECTION": frozenset({"model_selection_one_hot"}),
    "HYPERPARAMETER_OPTIMIZATION": frozenset({"hyperparameter_one_per_parameter"}),
    "CLUSTERING": frozenset({"ml_assignment", "ml_cluster_count"}),
}


class MLProblemType(Enum):
    """Supported AI/ML problem families.

    Attributes:
        CLASSIFICATION: Binary-coefficient least-squares classifier fit.
        REGRESSION: Binary-coefficient least-squares regression fit.
        FEATURE_SELECTION: Binary selection of a feature subset (delegated to
            the QMQ-09 Data layer).
        MODEL_SELECTION: One-hot selection of one candidate model.
        HYPERPARAMETER_OPTIMIZATION: One-hot choice per hyperparameter.
        CLUSTERING: Assignment of records to ``k`` clusters (delegated to the
            QMQ-09 Data layer).
    """

    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    FEATURE_SELECTION = "feature_selection"
    MODEL_SELECTION = "model_selection"
    HYPERPARAMETER_OPTIMIZATION = "hyperparameter_optimization"
    CLUSTERING = "clustering"

    @classmethod
    def parse(cls, value: Any) -> MLProblemType:
        """Coerce a name or member to a :class:`MLProblemType`."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower().replace("-", "_")
        for member in cls:
            if member.value == text or member.name.lower() == text:
                return member
        raise MLValidationError(
            f"unknown ML problem type {value!r}; expected one of: "
            f"{', '.join(member.value for member in cls)}"
        )


@dataclass
class MLProblem:
    """Domain problem of the AI/ML Intelligence layer.

    Args:
        name: Problem identifier.
        dataset: The ordered ML dataset (required for classification,
            regression, feature selection and clustering; optional for model
            selection and hyperparameter optimization).
        problem_type: Family (:class:`MLProblemType`).
        objectives: Ordered list of ML objectives (names must be unique).
        constraints: Ordered list of ML constraints (names must be unique).
        context: Optional ML context (purpose / strategy intent).
        candidates: Ordered model-selection candidates (model selection only).
        hyperparameters: Ordered hyperparameter space (hyperparameter
            optimization only).
        k: Number of clusters (clustering only).
        description: Free-form description.
        metadata: Free-form metadata (JSON-safe).

    Raises:
        MLValidationError: On duplicate objective/constraint names, invalid
            problem-type hyper-parameters or a dataset/candidate/parameters
            configuration mix-up.
    """

    name: str
    dataset: MLDataSet | None = None
    problem_type: MLProblemType = MLProblemType.CLASSIFICATION
    objectives: list[MLObjective] = field(default_factory=list)
    constraints: list[MLConstraint] = field(default_factory=list)
    context: MLContext | None = None
    candidates: list[MLModelCandidate] = field(default_factory=list)
    hyperparameters: list[MLHyperparameter] = field(default_factory=list)
    k: int | None = None
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        try:
            check_nonempty_name(self.name, label="ML problem name")
        except MLValidationError as exc:
            raise MLValidationError(str(exc)) from exc
        self.problem_type = MLProblemType.parse(self.problem_type)
        self._check_unique_names()
        problem_name = self.problem_type.name
        if (
            problem_name in _FITTING_TYPES or problem_name in _DELEGATED_TYPES
        ) and self.dataset is None:
            raise MLValidationError(f"{self.problem_type.value} problems require a dataset")
        if problem_name in _FITTING_TYPES:
            if self.candidates:
                raise MLValidationError("candidates are only valid for model-selection problems")
            if self.hyperparameters:
                raise MLValidationError(
                    "hyperparameters are only valid for hyperparameter problems"
                )
        if problem_name == "MODEL_SELECTION":
            if not self.candidates:
                raise MLValidationError("model-selection problems require at least one candidate")
            if self.hyperparameters:
                raise MLValidationError(
                    "hyperparameters are only valid for hyperparameter problems"
                )
        if problem_name == "HYPERPARAMETER_OPTIMIZATION":
            if not self.hyperparameters:
                raise MLValidationError(
                    "hyperparameter problems require at least one hyperparameter"
                )
            if self.candidates:
                raise MLValidationError("candidates are only valid for model-selection problems")
        if problem_name == "CLUSTERING":
            if self.k is None or int(self.k) < 1:
                raise MLValidationError("clustering problems require a positive cluster count (k)")
            if self.dataset is not None and int(self.k) > len(self.dataset.records):
                raise MLValidationError(
                    f"cluster count k={self.k} exceeds the {len(self.dataset.records)} records"
                )
        else:
            if self.k is not None:
                raise MLValidationError("k is only valid for clustering problems")

    @property
    def num_features(self) -> int:
        """Number of features of the underlying dataset."""
        return len(self.dataset.features) if self.dataset is not None else 0

    @property
    def num_records(self) -> int:
        """Number of records of the underlying dataset."""
        return len(self.dataset.records) if self.dataset is not None else 0

    @property
    def size(self) -> int:
        """Number of decision variables."""
        problem_name = self.problem_type.name
        if problem_name == "MODEL_SELECTION":
            return len(self.candidates)
        if problem_name == "HYPERPARAMETER_OPTIMIZATION":
            return sum(hyperparameter.choice_count for hyperparameter in self.hyperparameters)
        if problem_name == "CLUSTERING":
            return self.num_records * (self.k or 0)
        return self.num_features

    @property
    def hyperparameter_choice_counts(self) -> list[int]:
        """Return per-hyperparameter choice counts in deterministic order."""
        return [hyperparameter.choice_count for hyperparameter in self.hyperparameters]

    def _check_unique_names(self) -> None:
        objective_names = [objective.name for objective in self.objectives]
        constraint_names = [constraint.name for constraint in self.constraints]
        if len(set(objective_names)) != len(objective_names):
            raise MLValidationError("ML problem objective names must be unique")
        if len(set(constraint_names)) != len(constraint_names):
            raise MLValidationError("ML problem constraint names must be unique")

    def feature_variables(self) -> list[Variable]:
        """Return the binary coefficient variables ``w0 .. w{n-1}`` in feature order."""
        from quantsmind.quantum.core.variable import Variable

        dataset = self.dataset
        if dataset is None:
            raise MLValidationError("a dataset is required to build coefficient variables")
        return [
            Variable.binary(
                name=coefficient_variable_name(index),
                domain="ml.coefficient",
                description=f"fitting coefficient of feature {feature.name!r}",
            )
            for index, feature in enumerate(dataset.features)
        ]

    def selection_variables(self) -> list[Variable]:
        """Return the one-hot model-selection variables ``s0 .. s{n-1}``."""
        from quantsmind.quantum.core.variable import Variable

        return [
            Variable.binary(
                name=selection_variable_name(index),
                domain="ml.model",
                description=f"selection of candidate {candidate.model_id!r}",
            )
            for index, candidate in enumerate(self.candidates)
        ]

    def hyperparameter_variables(self) -> list[Variable]:
        """Return the one-hot hyperparameter choice variables (parameter-major)."""
        from quantsmind.quantum.core.variable import Variable

        variables: list[Variable] = []
        for param_index, hyperparameter in enumerate(self.hyperparameters):
            for choice_index in range(hyperparameter.choice_count):
                variables.append(
                    Variable.binary(
                        name=hyperparameter_variable_name(param_index, choice_index),
                        domain="ml.hyperparameter",
                        description=(
                            f"choice {choice_index} of hyperparameter {hyperparameter.name!r}"
                        ),
                    )
                )
        return variables

    def decision_variables(self) -> list[Variable]:
        """Return the deterministic decision-variable list for this problem.

        Fitting problems yield one binary variable per feature, model
        selection one binary variable per candidate and hyperparameter
        problems one binary variable per (parameter, choice) pair in
        parameter-major order.  Feature-selection and clustering problems are
        delegated to the QMQ-09 Data layer and expose no ML variables here.
        """
        problem_name = self.problem_type.name
        if problem_name == "MODEL_SELECTION":
            if not self.candidates:
                raise MLValidationError("cannot build model-selection variables without candidates")
            return self.selection_variables()
        if problem_name == "HYPERPARAMETER_OPTIMIZATION":
            if not self.hyperparameters:
                raise MLValidationError(
                    "cannot build hyperparameter variables without hyperparameters"
                )
            return self.hyperparameter_variables()
        if problem_name in _DELEGATED_TYPES:
            raise MLValidationError(
                f"{self.problem_type.value} is delegated to the QMQ-09 Data layer; "
                "use MLFormulationAdapter to build the delegated problem"
            )
        if self.dataset is None or not self.dataset.features:
            raise MLValidationError("cannot build coefficient variables without dataset features")
        return self.feature_variables()

    def validate(self) -> list[str]:
        """Return deterministic validation issues (never raises)."""
        issues: list[str] = []
        if self.dataset is not None:
            try:
                self.dataset.raise_if_invalid()
            except MLValidationError as exc:
                issues.append(str(exc))
        if not self.objectives:
            issues.append("ML problem has no objectives")
        problem_name = self.problem_type.name
        allowed_objectives = _ALLOWED_OBJECTIVE_KINDS.get(problem_name, frozenset())
        allowed_constraints = _ALLOWED_CONSTRAINT_KINDS.get(problem_name, frozenset())
        for objective in self.objectives:
            issues.extend(objective.validate(self))
            if allowed_objectives and objective.kind not in allowed_objectives:
                issues.append(
                    f"objective {objective.name!r} ({objective.kind}) is not valid for "
                    f"{self.problem_type.value}"
                )
        for constraint in self.constraints:
            issues.extend(constraint.validate(self))
            if allowed_constraints and constraint.kind not in allowed_constraints:
                issues.append(
                    f"constraint {constraint.name!r} ({constraint.kind}) is not valid for "
                    f"{self.problem_type.value}"
                )
        candidate_ids = [candidate.model_id for candidate in self.candidates]
        if len(set(candidate_ids)) != len(candidate_ids):
            issues.append("ML problem candidate ids must be unique")
        hyperparameter_names = [hyperparameter.name for hyperparameter in self.hyperparameters]
        if len(set(hyperparameter_names)) != len(hyperparameter_names):
            issues.append("ML problem hyperparameter names must be unique")
        return sorted(set(issue for issue in issues if issue))

    def raise_if_invalid(self) -> None:
        """Raise :class:`MLValidationError` with all validation issues."""
        issues = self.validate()
        if issues:
            raise MLValidationError(f"invalid ML problem {self.name!r}: " + "; ".join(issues))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "dataset": self.dataset.to_dict() if self.dataset is not None else None,
            "problem_type": self.problem_type.value,
            "objectives": [objective.to_dict() for objective in self.objectives],
            "constraints": [constraint.to_dict() for constraint in self.constraints],
            "context": self.context.to_dict() if self.context is not None else None,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "hyperparameters": [
                hyperparameter.to_dict() for hyperparameter in self.hyperparameters
            ],
            "k": int(self.k) if self.k is not None else None,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MLProblem:
        """Rebuild a problem from :meth:`to_dict` output."""
        dataset_data = data.get("dataset")
        context_data = data.get("context")
        return cls(
            name=str(data["name"]),
            description=str(data.get("description", "")),
            dataset=MLDataSet.from_dict(dict(dataset_data)) if dataset_data is not None else None,
            problem_type=MLProblemType.parse(data.get("problem_type", "classification")),
            objectives=[objective_from_dict(d) for d in data.get("objectives", [])],
            constraints=[constraint_from_dict(d) for d in data.get("constraints", [])],
            context=(MLContext.from_dict(dict(context_data)) if context_data is not None else None),
            candidates=[MLModelCandidate.from_dict(d) for d in data.get("candidates", [])],
            hyperparameters=[
                MLHyperparameter.from_dict(d) for d in data.get("hyperparameters", [])
            ],
            k=int(data["k"]) if data.get("k") is not None else None,
            metadata=dict(data.get("metadata", {})),
        )
