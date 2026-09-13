"""Machine learning formulation of quantum domain problems.

An :class:`MLModel` extends :class:`MathematicalModel` with a feature/
target schema so QMQ-02 can reason about quantum machine-learning
workflows (quantum kernels, variational classifiers) from a domain problem.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from quantsmind.quantum.formulation.mathematical_model import MathematicalModel

if TYPE_CHECKING:
    from quantsmind.quantum.core.problem import QuantumProblem


@dataclass
class MLModel(MathematicalModel):
    """Structural formulation of a machine learning problem.

    Args:
        features: Feature names/schema.
        target: Target column name.
        task: Learning task (e.g. ``"classification"``, ``"regression"``).
    """

    features: list[str] = field(default_factory=list)
    target: str = ""
    task: str = ""

    kind: ClassVar[str] = "ml"

    @classmethod
    def from_problem(cls, problem: QuantumProblem) -> MLModel:
        """Snapshot an ML problem (schema from problem metadata)."""
        model = super().from_problem(problem)
        model.features = [str(f) for f in problem.metadata.get("ml_features", [])]
        model.target = str(problem.metadata.get("ml_target", ""))
        model.task = str(problem.metadata.get("ml_task", ""))
        return model

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        data = super().to_dict()
        data["features"] = list(self.features)
        data["target"] = self.target
        data["task"] = self.task
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MLModel:
        """Rebuild an MLModel from :meth:`to_dict` output."""
        model = cls(
            name=str(data.get("name", "model")),
            problem_name=str(data.get("problem_name", "")),
            variables=[str(v) for v in data.get("variables", [])],
            objectives=[str(o) for o in data.get("objectives", [])],
            constraints=[str(c) for c in data.get("constraints", [])],
            metadata=dict(data.get("metadata", {})),
        )
        model.features = [str(f) for f in data.get("features", [])]
        model.target = str(data.get("target", ""))
        model.task = str(data.get("task", ""))
        return model


__all__ = ["MLModel"]
