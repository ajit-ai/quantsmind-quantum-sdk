"""Statistical formulation of quantum domain problems.

A :class:`StatisticalModel` extends :class:`MathematicalModel` with
distribution and assumption structure for problems where the goal is
statistical inference, hypothesis testing or data modelling (e.g.
quantum-enhanced estimation, Monte Carlo methods).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from quantsmind.quantum.formulation.mathematical_model import MathematicalModel

if TYPE_CHECKING:
    from quantsmind.quantum.core.problem import QuantumProblem


@dataclass
class StatisticalModel(MathematicalModel):
    """Structural formulation of a statistical problem.

    Args:
        distribution: Target distribution or family (e.g. ``"gaussian"``).
        assumptions: Statistical assumptions (e.g. ``["iid", "normal"]``).
    """

    distribution: str = ""
    assumptions: list[str] = field(default_factory=list)

    kind: ClassVar[str] = "statistical"

    @classmethod
    def from_problem(cls, problem: QuantumProblem) -> StatisticalModel:
        """Snapshot a statistical problem (config from problem metadata)."""
        model = super().from_problem(problem)
        model.distribution = str(problem.metadata.get("statistical_distribution", ""))
        model.assumptions = [str(a) for a in problem.metadata.get("statistical_assumptions", [])]
        return model

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        data = super().to_dict()
        data["distribution"] = self.distribution
        data["assumptions"] = list(self.assumptions)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StatisticalModel:
        """Rebuild a StatisticalModel from :meth:`to_dict` output."""
        model = cls(
            name=str(data.get("name", "model")),
            problem_name=str(data.get("problem_name", "")),
            variables=[str(v) for v in data.get("variables", [])],
            objectives=[str(o) for o in data.get("objectives", [])],
            constraints=[str(c) for c in data.get("constraints", [])],
            metadata=dict(data.get("metadata", {})),
        )
        model.distribution = str(data.get("distribution", ""))
        model.assumptions = [str(a) for a in data.get("assumptions", [])]
        return model


__all__ = ["StatisticalModel"]
