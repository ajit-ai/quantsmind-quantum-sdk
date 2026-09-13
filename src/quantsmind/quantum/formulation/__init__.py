"""Formulation layer of QuantsMind Quantum.

The formulation layer translates a domain problem into a structured
mathematical representation.  Each model type extends
:class:`MathematicalModel` with family-specific detail.
"""

from __future__ import annotations

from typing import Any, cast

from quantsmind.quantum.formulation.graph_model import GraphModel
from quantsmind.quantum.formulation.mathematical_model import MathematicalModel
from quantsmind.quantum.formulation.ml_model import MLModel
from quantsmind.quantum.formulation.optimization_model import OptimizationModel
from quantsmind.quantum.formulation.simulation_model import SimulationModel
from quantsmind.quantum.formulation.statistical_model import StatisticalModel

__all__ = [
    "MathematicalModel",
    "OptimizationModel",
    "GraphModel",
    "MLModel",
    "SimulationModel",
    "StatisticalModel",
    "formulate",
    "model_from_dict",
]

# Formulation kind -> class, used by :func:`model_from_dict`.
_MODEL_KINDS: dict[str, type[MathematicalModel]] = {
    cls.kind: cls
    for cls in (
        MathematicalModel,
        OptimizationModel,
        GraphModel,
        MLModel,
        SimulationModel,
        StatisticalModel,
    )
}


def formulate(problem: Any) -> MathematicalModel:
    """Select and return the appropriate formulation for a domain problem.

    Uses deterministic, rule-based logic based on ``problem.metadata``
    and problem contents.  Returns the existing ``problem.formulation``
    when already set.
    """
    if problem.formulation is not None:
        return cast(MathematicalModel, problem.formulation)
    meta = problem.metadata if isinstance(problem.metadata, dict) else {}
    kind = meta.get("model_kind")
    if kind == "graph":
        return GraphModel.from_problem(problem)
    if kind == "ml":
        return MLModel.from_problem(problem)
    if kind == "simulation":
        return SimulationModel.from_problem(problem)
    if kind == "statistical":
        return StatisticalModel.from_problem(problem)
    if kind == "optimization" or problem.objectives or problem.constraints:
        return OptimizationModel.from_problem(problem)
    return MathematicalModel.from_problem(problem)


def model_from_dict(data: dict[str, Any]) -> MathematicalModel:
    """Reconstruct a formulation model from its serialized ``kind``."""
    kind = data.get("kind", "mathematical")
    cls = _MODEL_KINDS.get(kind)
    if cls is None:
        raise ValueError(f"unknown formulation kind {kind!r}")
    return cls.from_dict(data)
