"""Simulation formulation of quantum domain problems.

A :class:`SimulationModel` extends :class:`MathematicalModel` with
time-step/dynamics structure for simulating the evolution of a system
over time (physical, chemical, biological or market dynamics).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

from quantsmind.quantum.formulation.mathematical_model import MathematicalModel

if TYPE_CHECKING:
    from quantsmind.quantum.core.problem import QuantumProblem


@dataclass
class SimulationModel(MathematicalModel):
    """Structural formulation of a simulation problem.

    Args:
        time_steps: Number of discrete evolution steps.
        dynamics: Description of the evolution law (e.g. ``"hamiltonian"``,
            ``"reaction-diffusion"``).
    """

    time_steps: int = 0
    dynamics: str = ""

    kind: ClassVar[str] = "simulation"

    @classmethod
    def from_problem(cls, problem: QuantumProblem) -> SimulationModel:
        """Snapshot a simulation problem (solver config from metadata)."""
        model = super().from_problem(problem)
        model.time_steps = int(problem.metadata.get("simulation_steps", 0))
        model.dynamics = str(problem.metadata.get("simulation_dynamics", ""))
        return model

    @property
    def n_steps(self) -> int:
        """Number of evolution steps."""
        return self.time_steps

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        data = super().to_dict()
        data["time_steps"] = self.time_steps
        data["dynamics"] = self.dynamics
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SimulationModel:
        """Rebuild a SimulationModel from :meth:`to_dict` output."""
        model = cls(
            name=str(data.get("name", "model")),
            problem_name=str(data.get("problem_name", "")),
            variables=[str(v) for v in data.get("variables", [])],
            objectives=[str(o) for o in data.get("objectives", [])],
            constraints=[str(c) for c in data.get("constraints", [])],
            metadata=dict(data.get("metadata", {})),
        )
        model.time_steps = int(data.get("time_steps", 0))
        model.dynamics = str(data.get("dynamics", ""))
        return model


__all__ = ["SimulationModel"]
