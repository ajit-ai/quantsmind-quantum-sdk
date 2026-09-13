"""Graph formulation of quantum domain problems.

A :class:`GraphModel` extends :class:`MathematicalModel` with graph
structure (nodes and edges) for problems such as maximum independent set,
graph coloring, community detection or network optimization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from quantsmind.quantum.formulation.mathematical_model import MathematicalModel

if TYPE_CHECKING:
    from quantsmind.quantum.core.problem import QuantumProblem


@dataclass
class GraphModel(MathematicalModel):
    """Structural formulation of a graph problem.

    Args:
        nodes: Names/labels of graph nodes.
        edges: Undirected edge pairs ``(source, target)``.
    """

    nodes: list[str] = field(default_factory=list)
    edges: list[tuple[str, str]] = field(default_factory=list)

    kind: ClassVar[str] = "graph"

    @classmethod
    def from_problem(cls, problem: QuantumProblem) -> GraphModel:
        """Snapshot a graph problem (nodes/edges from problem metadata)."""
        model = super().from_problem(problem)
        model.nodes = [str(n) for n in problem.metadata.get("graph_nodes", [])]
        model.edges = [(str(a), str(b)) for a, b in problem.metadata.get("graph_edges", [])]
        return model

    @property
    def n_nodes(self) -> int:
        """Number of graph nodes."""
        return len(self.nodes)

    @property
    def n_edges(self) -> int:
        """Number of graph edges."""
        return len(self.edges)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        data = super().to_dict()
        data["nodes"] = list(self.nodes)
        data["edges"] = [list(edge) for edge in self.edges]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GraphModel:
        """Rebuild a GraphModel from :meth:`to_dict` output."""
        model = cls(
            name=str(data.get("name", "model")),
            problem_name=str(data.get("problem_name", "")),
            variables=[str(v) for v in data.get("variables", [])],
            objectives=[str(o) for o in data.get("objectives", [])],
            constraints=[str(c) for c in data.get("constraints", [])],
            metadata=dict(data.get("metadata", {})),
        )
        model.nodes = [str(n) for n in data.get("nodes", [])]
        model.edges = [(str(a), str(b)) for a, b in data.get("edges", [])]
        return model


__all__ = ["GraphModel"]
