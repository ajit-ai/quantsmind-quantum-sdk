"""QMQ-10 ML-domain mappings.

The mapper translates the domain ML variable naming conventions (``w<i>`` for
fitting coefficients, ``s<c>`` for model selection, ``h{p}_{c}`` for
hyperparameter choices) into a deterministic :class:`MLMapping` that decodes
QMQ assignments back into domain-readable decisions.

Feature-selection and clustering problems are delegated: their mapping and
decoding are performed by the QMQ-09 Data mapper on the delegated
``DataProblem``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from quantsmind.quantum.ml._expr import (
    coefficient_variable_name,
    hyperparameter_variable_name,
    selection_variable_name,
)
from quantsmind.quantum.ml.problem import MLProblem, MLProblemType

__all__ = [
    "DecodedMLCoefficient",
    "DecodedModelSelection",
    "DecodedHyperparameterChoice",
    "MLMapping",
    "MLMapper",
]


@dataclass
class DecodedMLCoefficient:
    """One decoded fitting-coefficient decision.

    Attributes:
        feature_name: Domain feature name.
        index: Deterministic feature index.
        variable_name: QMQ variable name (``w<i>``).
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
class DecodedModelSelection:
    """One decoded model-selection decision.

    Attributes:
        model_id: Domain candidate identifier.
        index: Deterministic candidate index.
        variable_name: QMQ variable name (``s<c>``).
        value: Raw assignment value (0.0 or 1.0).
        selected: Whether the value exceeds the selection threshold.
    """

    model_id: str
    index: int
    variable_name: str
    value: float
    selected: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "index": self.index,
            "variable_name": self.variable_name,
            "value": float(self.value),
            "selected": bool(self.selected),
        }


@dataclass
class DecodedHyperparameterChoice:
    """One decoded hyperparameter-choice decision.

    Attributes:
        parameter_name: Domain hyperparameter name.
        param_index: Deterministic parameter index.
        choice_index: Deterministic choice index.
        choice_value: The concrete choice value (JSON-safe).
        variable_name: QMQ variable name (``h{p}_{c}``).
        value: Raw assignment value (0.0 or 1.0).
        selected: Whether the value exceeds the selection threshold.
    """

    parameter_name: str
    param_index: int
    choice_index: int
    choice_value: Any
    variable_name: str
    value: float
    selected: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "parameter_name": self.parameter_name,
            "param_index": self.param_index,
            "choice_index": self.choice_index,
            "choice_value": self.choice_value,
            "variable_name": self.variable_name,
            "value": float(self.value),
            "selected": bool(self.selected),
        }


@dataclass
class MLMapping:
    """Deterministic mapping between ML variables and QMQ indices.

    Created by :meth:`MLMapper.map` from a validated :class:`MLProblem`.
    """

    problem_name: str
    problem_type: MLProblemType
    feature_order: list[str]
    candidate_order: list[str]
    parameter_order: list[str]
    choice_values: dict[str, list[Any]] | None = None

    def __post_init__(self) -> None:
        self.problem_type = MLProblemType.parse(self.problem_type)

    @property
    def variable_names(self) -> list[str]:
        """QMQ variable names in deterministic order."""
        problem_name = self.problem_type.name
        if problem_name == "MODEL_SELECTION":
            return [selection_variable_name(index) for index in range(len(self.candidate_order))]
        if problem_name == "HYPERPARAMETER_OPTIMIZATION":
            values = self.choice_values or {}
            names: list[str] = []
            for param_index, parameter in enumerate(self.parameter_order):
                for choice_index in range(len(values.get(parameter, []))):
                    names.append(hyperparameter_variable_name(param_index, choice_index))
            return names
        return [coefficient_variable_name(index) for index in range(len(self.feature_order))]

    def coefficient(self, feature_name: str) -> DecodedMLCoefficient | None:
        """Return the decoded coefficient for ``feature_name`` (or ``None``)."""
        if feature_name not in self.feature_order:
            return None
        index = self.feature_order.index(feature_name)
        return DecodedMLCoefficient(
            feature_name=feature_name,
            index=index,
            variable_name=coefficient_variable_name(index),
            value=0.0,
            selected=False,
        )

    def candidate(self, model_id: str) -> DecodedModelSelection | None:
        """Return the decoded model selection for ``model_id`` (or ``None``)."""
        if model_id not in self.candidate_order:
            return None
        index = self.candidate_order.index(model_id)
        return DecodedModelSelection(
            model_id=model_id,
            index=index,
            variable_name=selection_variable_name(index),
            value=0.0,
            selected=False,
        )

    def decode_assignments(
        self,
        assignments: dict[str, float],
        *,
        selected_threshold: float = 0.5,
    ) -> list[Any]:
        """Decode raw QMQ assignments into domain-readable decisions."""
        problem_name = self.problem_type.name
        if problem_name == "MODEL_SELECTION":
            return self._decode_model_selection(assignments, selected_threshold=selected_threshold)
        if problem_name == "HYPERPARAMETER_OPTIMIZATION":
            return self._decode_hyperparameters(assignments, selected_threshold=selected_threshold)
        return self._decode_coefficients(assignments, selected_threshold=selected_threshold)

    def _decode_coefficients(
        self,
        assignments: dict[str, float],
        *,
        selected_threshold: float,
    ) -> list[DecodedMLCoefficient]:
        decoded: list[DecodedMLCoefficient] = []
        for index, feature_name in enumerate(self.feature_order):
            variable_name = coefficient_variable_name(index)
            value = float(assignments.get(variable_name, 0.0))
            decoded.append(
                DecodedMLCoefficient(
                    feature_name=feature_name,
                    index=index,
                    variable_name=variable_name,
                    value=value,
                    selected=value >= selected_threshold,
                )
            )
        return decoded

    def _decode_model_selection(
        self,
        assignments: dict[str, float],
        *,
        selected_threshold: float,
    ) -> list[DecodedModelSelection]:
        decoded: list[DecodedModelSelection] = []
        for index, model_id in enumerate(self.candidate_order):
            variable_name = selection_variable_name(index)
            value = float(assignments.get(variable_name, 0.0))
            decoded.append(
                DecodedModelSelection(
                    model_id=model_id,
                    index=index,
                    variable_name=variable_name,
                    value=value,
                    selected=value >= selected_threshold,
                )
            )
        return decoded

    def _decode_hyperparameters(
        self,
        assignments: dict[str, float],
        *,
        selected_threshold: float,
    ) -> list[DecodedHyperparameterChoice]:
        values = self.choice_values or {}
        decoded: list[DecodedHyperparameterChoice] = []
        for param_index, parameter in enumerate(self.parameter_order):
            choices = values.get(parameter, [])
            for choice_index in range(len(choices)):
                variable_name = hyperparameter_variable_name(param_index, choice_index)
                value = float(assignments.get(variable_name, 0.0))
                decoded.append(
                    DecodedHyperparameterChoice(
                        parameter_name=parameter,
                        param_index=param_index,
                        choice_index=choice_index,
                        choice_value=choices[choice_index],
                        variable_name=variable_name,
                        value=value,
                        selected=value >= selected_threshold,
                    )
                )
        return decoded


@dataclass
class MLMapper:
    """Maps a validated ML problem to a deterministic variable mapping.

    Mirrors the :class:`DataMapper` pattern: validates, then provides
    :meth:`map` (which returns an :class:`MLMapping`) and
    :meth:`decode_assignments` (which directly returns decoded decisions).
    """

    def map(self, problem: MLProblem) -> MLMapping:
        """Return the deterministic variable mapping of ``problem``.

        Raises:
            MLValidationError: If the problem is delegated to the QMQ-09 Data
                layer (use the Data mapper on the delegated problem).
        """
        problem.raise_if_invalid()
        if problem.problem_type is MLProblemType.FEATURE_SELECTION or (
            problem.problem_type is MLProblemType.CLUSTERING
        ):
            from quantsmind.quantum.ml.errors import MLValidationError

            raise MLValidationError(
                f"{problem.problem_type.value} is delegated to the QMQ-09 Data layer; "
                "use MLFormulationAdapter.to_data_problem and the Data mapper"
            )
        choice_values: dict[str, list[Any]] | None = None
        if problem.problem_type is MLProblemType.HYPERPARAMETER_OPTIMIZATION:
            choice_values = {
                hyperparameter.name: [choice.value for choice in hyperparameter.choices]
                for hyperparameter in problem.hyperparameters
            }
        return MLMapping(
            problem_name=problem.name,
            problem_type=problem.problem_type,
            feature_order=list(problem.dataset.feature_names)
            if problem.dataset is not None
            else [],
            candidate_order=[candidate.model_id for candidate in problem.candidates],
            parameter_order=[hyperparameter.name for hyperparameter in problem.hyperparameters],
            choice_values=choice_values,
        )

    def decode_assignments(
        self,
        problem: MLProblem,
        assignments: dict[str, float],
        *,
        selected_threshold: float = 0.5,
    ) -> list[Any]:
        """Decode raw QMQ assignments into domain-readable decisions."""
        return self.map(problem).decode_assignments(
            assignments, selected_threshold=selected_threshold
        )
