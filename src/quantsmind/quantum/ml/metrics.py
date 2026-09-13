"""ML-metrics computation of the QMQ-10 AI/ML Intelligence layer.

:class:`MLMetrics` summarises the domain outcome of an ML solve: the sum of
squared residuals of a fitting problem, the selected model's scores, the
total gain of the selected hyperparameter configuration and the existing
QMQ-05 constraint-violation counts.  Computations are deterministic and
reuse the QMQ-05 :func:`constraint_violations` accounting at the solution
construction site (never recomputed ad hoc here).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from quantsmind.quantum.ml.mapping import (
    DecodedHyperparameterChoice,
    DecodedMLCoefficient,
    DecodedModelSelection,
    MLMapper,
)
from quantsmind.quantum.ml.problem import MLProblem

__all__ = ["MLMetrics"]


@dataclass
class MLMetrics:
    """Deterministic outcome metrics of an ML solve.

    Attributes:
        problem_type: ML problem family (``"classification"``,
            ``"regression"``, ``"model_selection"`` or
            ``"hyperparameter_optimization"``).
        ssr: Sum of squared residuals of the fitted linear model (fitting).
        mse: Mean squared error (``ssr / num_records``, fitting).
        selected_feature_count: Number of selected coefficients (fitting).
        selected_model_id: Selected candidate identifier (model selection).
        selected_loss: Validation loss of the selected candidate.
        selected_penalty: Complexity penalty of the selected candidate.
        total_gain: Total gain of the selected hyperparameter configuration.
        objective_value: Primary objective value decoded from the assignment.
        constraint_violations: Number of violated QMQ constraints.
        constraint_violation_magnitude: Aggregate violation magnitude.
        metadata: Free-form metadata (JSON-safe).
    """

    problem_type: str = ""
    ssr: float | None = None
    mse: float | None = None
    selected_feature_count: int = 0
    selected_model_id: str = ""
    selected_loss: float | None = None
    selected_penalty: float | None = None
    total_gain: float | None = None
    objective_value: float | None = None
    constraint_violations: int = 0
    constraint_violation_magnitude: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def compute(
        cls,
        problem: MLProblem,
        assignments: dict[str, float],
        *,
        selected_threshold: float = 0.5,
        violation_count: int = 0,
        violation_magnitude: float = 0.0,
    ) -> MLMetrics:
        """Compute deterministic metrics from raw QMQ assignments."""
        mapping = MLMapper().map(problem)
        decoded = mapping.decode_assignments(assignments, selected_threshold=selected_threshold)
        problem_name = problem.problem_type.name
        if problem_name in ("CLASSIFICATION", "REGRESSION"):
            return cls._fitting(problem, decoded, violation_count, violation_magnitude)
        if problem_name == "MODEL_SELECTION":
            return cls._model_selection(problem, decoded, violation_count, violation_magnitude)
        return cls._hyperparameters(problem, decoded, violation_count, violation_magnitude)

    @classmethod
    def _fitting(
        cls,
        problem: MLProblem,
        decoded: list[Any],
        violation_count: int,
        violation_magnitude: float,
    ) -> MLMetrics:
        selected = [
            item for item in decoded if isinstance(item, DecodedMLCoefficient) and item.selected
        ]
        selected_names = {item.feature_name for item in selected}
        dataset = problem.dataset
        matrix = dataset.matrix() if dataset is not None else []
        targets = dataset.targets() if dataset is not None else []
        feature_names = dataset.feature_names if dataset is not None else []
        index_of_name = {name: index for index, name in enumerate(feature_names)}
        ssr = 0.0
        for record, target in zip(matrix, targets, strict=True):
            prediction = sum(
                float(record[index_of_name[name]])
                for name in selected_names
                if name in index_of_name
            )
            residual = float(target) - prediction
            ssr += residual * residual
        num_records = max(len(targets), 1)
        return cls(
            problem_type=problem.problem_type.value,
            ssr=ssr,
            mse=ssr / num_records,
            selected_feature_count=len(selected),
            objective_value=ssr,
            constraint_violations=int(violation_count),
            constraint_violation_magnitude=float(violation_magnitude),
        )

    @classmethod
    def _model_selection(
        cls,
        problem: MLProblem,
        decoded: list[Any],
        violation_count: int,
        violation_magnitude: float,
    ) -> MLMetrics:
        selected = [
            item for item in decoded if isinstance(item, DecodedModelSelection) and item.selected
        ]
        candidate_by_id = {candidate.model_id: candidate for candidate in problem.candidates}
        model_id = selected[0].model_id if selected else ""
        candidate = candidate_by_id.get(model_id)
        objective_value = candidate.objective() if candidate is not None else None
        return cls(
            problem_type=problem.problem_type.value,
            selected_model_id=model_id,
            selected_loss=float(candidate.validation_loss) if candidate is not None else None,
            selected_penalty=(
                float(candidate.complexity_penalty) if candidate is not None else None
            ),
            objective_value=objective_value,
            constraint_violations=int(violation_count),
            constraint_violation_magnitude=float(violation_magnitude),
        )

    @classmethod
    def _hyperparameters(
        cls,
        problem: MLProblem,
        decoded: list[Any],
        violation_count: int,
        violation_magnitude: float,
    ) -> MLMetrics:
        selected = [
            item
            for item in decoded
            if isinstance(item, DecodedHyperparameterChoice) and item.selected
        ]
        gain_by_index = {
            (param_index, choice_index): float(choice.gain)
            for param_index, hyperparameter in enumerate(problem.hyperparameters)
            for choice_index, choice in enumerate(hyperparameter.choices)
        }
        total_gain = sum(
            gain_by_index.get((item.param_index, item.choice_index), 0.0) for item in selected
        )
        return cls(
            problem_type=problem.problem_type.value,
            total_gain=total_gain,
            objective_value=total_gain,
            constraint_violations=int(violation_count),
            constraint_violation_magnitude=float(violation_magnitude),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "problem_type": self.problem_type,
            "ssr": self.ssr,
            "mse": self.mse,
            "selected_feature_count": int(self.selected_feature_count),
            "selected_model_id": self.selected_model_id,
            "selected_loss": self.selected_loss,
            "selected_penalty": self.selected_penalty,
            "total_gain": self.total_gain,
            "objective_value": self.objective_value,
            "constraint_violations": int(self.constraint_violations),
            "constraint_violation_magnitude": float(self.constraint_violation_magnitude),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MLMetrics:
        """Rebuild metrics from :meth:`to_dict` output."""
        return cls(
            problem_type=str(data.get("problem_type", "")),
            ssr=(float(data["ssr"]) if data.get("ssr") is not None else None),
            mse=(float(data["mse"]) if data.get("mse") is not None else None),
            selected_feature_count=int(data.get("selected_feature_count", 0)),
            selected_model_id=str(data.get("selected_model_id", "")),
            selected_loss=(
                float(data["selected_loss"]) if data.get("selected_loss") is not None else None
            ),
            selected_penalty=(
                float(data["selected_penalty"])
                if data.get("selected_penalty") is not None
                else None
            ),
            total_gain=(float(data["total_gain"]) if data.get("total_gain") is not None else None),
            objective_value=(
                float(data["objective_value"]) if data.get("objective_value") is not None else None
            ),
            constraint_violations=int(data.get("constraint_violations", 0)),
            constraint_violation_magnitude=float(data.get("constraint_violation_magnitude", 0.0)),
            metadata=dict(data.get("metadata", {})),
        )
