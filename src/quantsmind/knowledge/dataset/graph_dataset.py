"""
Graph Dataset Module

This module provides graph dataset definitions for the Knowledge package.

Purpose
-------
Provide graph dataset management with network/graph data support.

Responsibilities
----------------
- Define graph dataset structure
- Support graph data
- Support graph operations
- Support graph metadata
- Support graph validation

Dependencies
------------
typing (standard library)
quantsmind.knowledge.dataset.dataset (dataset)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.knowledge.dataset.dataset import Dataset
from quantsmind.knowledge.enums import DatasetType
from quantsmind.knowledge.exceptions import DatasetError
from quantsmind.knowledge.types import (
    DatasetData,
    DatasetSchema,
    ValidationResult,
)


class GraphDataset(Dataset):
    """Concrete implementation of a graph dataset.

    This class provides graph dataset functionality with network/graph data support.

    Attributes:
        _graphs: Graph records
        _node_count: Number of nodes
        _edge_count: Number of edges
        _graph_type: Graph type (directed, undirected)

    Example:
        >>> dataset = GraphDataset("graph_data", graph_type="undirected")
        >>> dataset.add_graph({"nodes": [1, 2, 3], "edges": [(1, 2), (2, 3)]})
    """

    def __init__(
        self,
        name: str,
        graph_type: str = "undirected",
        schema: DatasetSchema | None = None,
        data: DatasetData | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a GraphDataset.

        Args:
            name: Dataset name
            graph_type: Graph type (directed, undirected)
            schema: Dataset schema
            data: Dataset data
            metadata: Dataset metadata

        Example:
            >>> dataset = GraphDataset("graph_data", graph_type="undirected")
        """
        super().__init__(
            name=name,
            dataset_type=DatasetType.GRAPH,
            schema=schema,
            data=data,
            metadata=metadata,
        )
        if graph_type not in ["directed", "undirected"]:
            raise DatasetError("Graph type must be 'directed' or 'undirected'", {"graph_type": graph_type})

        self._graph_type = graph_type
        self._node_count = 0
        self._edge_count = 0
        self._graphs: list[dict[str, Any]] = []

    @property
    def graph_type(self) -> str:
        """Get the graph type.

        Returns:
            Graph type

        Example:
            >>> gtype = dataset.graph_type
        """
        return self._graph_type

    @property
    def node_count(self) -> int:
        """Get the node count.

        Returns:
            Number of nodes

        Example:
            >>> nodes = dataset.node_count
        """
        return self._node_count

    @property
    def edge_count(self) -> int:
        """Get the edge count.

        Returns:
            Number of edges

        Example:
            >>> edges = dataset.edge_count
        """
        return self._edge_count

    @property
    def graphs(self) -> list[dict[str, Any]]:
        """Get the graphs.

        Returns:
            Graph records

        Example:
            >>> graphs = dataset.graphs
        """
        return self._graphs.copy()

    def add_graph(self, graph: dict[str, Any]) -> None:
        """Add a graph to the dataset.

        Args:
            graph: Graph data

        Raises:
            DatasetError: If graph is invalid

        Example:
            >>> dataset.add_graph({"nodes": [1, 2, 3], "edges": [(1, 2), (2, 3)]})
        """
        if not isinstance(graph, dict):
            raise DatasetError("Graph must be a dictionary", {"graph": graph})

        nodes = graph.get("nodes")
        edges = graph.get("edges")

        if nodes is None:
            raise DatasetError("Graph must have nodes", {"graph": graph})

        if not isinstance(nodes, list):
            raise DatasetError("Nodes must be a list", {"nodes": nodes})

        if edges is not None and not isinstance(edges, list):
            raise DatasetError("Edges must be a list", {"edges": edges})

        self._graphs.append(graph)
        self._node_count += len(nodes)
        if edges:
            self._edge_count += len(edges)
        self._updated_at = self._updated_at

    def add_graphs(self, graphs: list[dict[str, Any]]) -> None:
        """Add multiple graphs to the dataset.

        Args:
            graphs: Graph data list

        Example:
            >>> dataset.add_graphs([{"nodes": [1, 2]}, {"nodes": [3, 4]}])
        """
        for graph in graphs:
            self.add_graph(graph)

    def get_graph_by_index(self, index: int) -> dict[str, Any] | None:
        """Get graph by index.

        Args:
            index: Graph index

        Returns:
            Graph data or None

        Example:
            >>> graph = dataset.get_graph_by_index(0)
        """
        if 0 <= index < len(self._graphs):
            return self._graphs[index]
        return None

    def get_graphs_by_node_count(self, min_nodes: int, max_nodes: int | None = None) -> list[dict[str, Any]]:
        """Get graphs with specific node count range.

        Args:
            min_nodes: Minimum node count
            max_nodes: Maximum node count (optional)

        Returns:
            Graph records

        Example:
            >>> graphs = dataset.get_graphs_by_node_count(10, 20)
        """
        result = []
        for graph in self._graphs:
            nodes = len(graph.get("nodes", []))
            if nodes >= min_nodes and (max_nodes is None or nodes <= max_nodes):
                result.append(graph)
        return result

    def calculate_graph_statistics(self, graph_index: int) -> dict[str, Any]:
        """Calculate statistics for a graph.

        Args:
            graph_index: Graph index

        Returns:
            Statistics dictionary

        Example:
            >>> stats = dataset.calculate_graph_statistics(0)
        """
        if graph_index >= len(self._graphs):
            return {}

        graph = self._graphs[graph_index]
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        if not nodes:
            return {}

        # Calculate degree
        degree_map = {}
        for edge in edges:
            if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                source, target = edge[0], edge[1]
                degree_map[source] = degree_map.get(source, 0) + 1
                if self._graph_type == "undirected":
                    degree_map[target] = degree_map.get(target, 0) + 1

        degrees = list(degree_map.values())
        avg_degree = sum(degrees) / len(degrees) if degrees else 0

        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "average_degree": avg_degree,
            "max_degree": max(degrees) if degrees else 0,
            "min_degree": min(degrees) if degrees else 0,
        }

    def find_connected_components(self, graph_index: int) -> list[list[Any]]:
        """Find connected components in a graph.

        Args:
            graph_index: Graph index

        Returns:
            List of connected components

        Example:
            >>> components = dataset.find_connected_components(0)
        """
        if graph_index >= len(self._graphs):
            return []

        graph = self._graphs[graph_index]
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        if not nodes:
            return []

        # Build adjacency list
        adjacency = {node: [] for node in nodes}
        for edge in edges:
            if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                source, target = edge[0], edge[1]
                if source in adjacency:
                    adjacency[source].append(target)
                if self._graph_type == "undirected" and target in adjacency:
                    adjacency[target].append(source)

        # Find connected components using BFS
        visited = set()
        components = []

        for node in nodes:
            if node not in visited:
                component = []
                queue = [node]
                visited.add(node)

                while queue:
                    current = queue.pop(0)
                    component.append(current)

                    for neighbor in adjacency.get(current, []):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)

                components.append(component)

        return components

    def validate(self) -> ValidationResult:
        """Validate the graph dataset.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = dataset.validate()
        """
        errors = []

        # Validate base dataset
        base_valid, base_errors = super().validate()
        errors.extend(base_errors)

        # Validate graphs
        for i, graph in enumerate(self._graphs):
            if "nodes" not in graph:
                errors.append(f"Graph {i} missing nodes")

            nodes = graph.get("nodes")
            if nodes and not isinstance(nodes, list):
                errors.append(f"Graph {i} nodes must be a list")

            edges = graph.get("edges")
            if edges and not isinstance(edges, list):
                errors.append(f"Graph {i} edges must be a list")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dataset definition

        Example:
            >>> data = dataset.to_dict()
        """
        data = super().to_dict()
        data.update({
            "graph_type": self._graph_type,
            "node_count": self._node_count,
            "edge_count": self._edge_count,
            "graphs_count": len(self._graphs),
        })
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(dataset)
        """
        return f"GraphDataset(id={self._id}, name={self._name}, type={self._graph_type}, nodes={self._node_count}, edges={self._edge_count}, graphs={len(self._graphs)})"


# Export
__all__ = [
    "GraphDataset",
]
