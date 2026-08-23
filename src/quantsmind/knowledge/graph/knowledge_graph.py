"""
Knowledge Graph Module

This module provides knowledge graph definitions for the Knowledge package.

Purpose
-------
Provide knowledge graph management and operations.

Responsibilities
----------------
- Define knowledge graph structure
- Support graph operations
- Support graph traversal
- Support graph validation

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.interfaces (knowledge interfaces)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.knowledge.enums import GraphType
from quantsmind.knowledge.exceptions import GraphError
from quantsmind.knowledge.interfaces import IGraph
from quantsmind.knowledge.types import (
    EdgeData,
    GraphID,
    NodeData,
    Path,
    ValidationResult,
)


class KnowledgeGraph(IGraph):
    """Concrete implementation of a knowledge graph.

    This class provides knowledge graph functionality.

    Attributes:
        _id: Graph ID
        _graph_type: Graph type
        _nodes: Graph nodes
        _edges: Graph edges
        _adjacency: Adjacency list
        _metadata: Graph metadata

    Example:
        >>> graph = KnowledgeGraph("graph_001", GraphType.KNOWLEDGE)
        >>> graph.add_node("node_001", {"label": "Entity"})
    """

    def __init__(
        self,
        graph_id: GraphID,
        graph_type: GraphType = GraphType.KNOWLEDGE,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a KnowledgeGraph.

        Args:
            graph_id: Graph ID
            graph_type: Graph type
            metadata: Graph metadata

        Example:
            >>> graph = KnowledgeGraph("graph_001", GraphType.KNOWLEDGE)
        """
        self._id = graph_id
        self._graph_type = graph_type
        self._nodes: dict[str, NodeData] = {}
        self._edges: dict[tuple[str, str], EdgeData] = {}
        self._adjacency: dict[str, list[tuple[str, EdgeData]]] = {}
        self._metadata = metadata or {}

    @property
    def id(self) -> GraphID:
        """Get the graph ID.

        Returns:
            Graph ID

        Example:
            >>> graph_id = graph.id
        """
        return self._id

    @property
    def graph_type(self) -> GraphType:
        """Get the graph type.

        Returns:
            Graph type

        Example:
            >>> gtype = graph.graph_type
        """
        return self._graph_type

    @property
    def nodes(self) -> dict[str, NodeData]:
        """Get the nodes.

        Returns:
            Nodes dictionary

        Example:
            >>> nodes = graph.nodes
        """
        return self._nodes.copy()

    @property
    def edges(self) -> dict[tuple[str, str], EdgeData]:
        """Get the edges.

        Returns:
            Edges dictionary

        Example:
            >>> edges = graph.edges
        """
        return self._edges.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the graph metadata.

        Returns:
            Graph metadata

        Example:
            >>> metadata = graph.metadata
        """
        return self._metadata.copy()

    def add_node(self, node_id: str, data: NodeData | None = None) -> None:
        """Add a node to the graph.

        Args:
            node_id: Node ID
            data: Node data

        Example:
            >>> graph.add_node("node_001", {"label": "Entity"})
        """
        if not node_id:
            raise GraphError("Node ID cannot be empty", {"node_id": node_id})

        self._nodes[node_id] = data or {}
        if node_id not in self._adjacency:
            self._adjacency[node_id] = []

    def add_edge(self, source: str, target: str, data: EdgeData | None = None) -> None:
        """Add an edge to the graph.

        Args:
            source: Source node
            target: Target node
            data: Edge data

        Example:
            >>> graph.add_edge("node_001", "node_002", {"type": "related"})
        """
        if source not in self._nodes:
            raise GraphError("Source node not found", {"source": source})

        if target not in self._nodes:
            raise GraphError("Target node not found", {"target": target})

        edge_key = (source, target)
        self._edges[edge_key] = data or {}
        self._adjacency[source].append((target, data or {}))

    def get_node(self, node_id: str) -> NodeData | None:
        """Get a node from the graph.

        Args:
            node_id: Node ID

        Returns:
            Node data or None

        Example:
            >>> node = graph.get_node("node_001")
        """
        return self._nodes.get(node_id)

    def get_edge(self, source: str, target: str) -> EdgeData | None:
        """Get an edge from the graph.

        Args:
            source: Source node
            target: Target node

        Returns:
            Edge data or None

        Example:
            >>> edge = graph.get_edge("node_001", "node_002")
        """
        return self._edges.get((source, target))

    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the graph.

        Args:
            node_id: Node ID

        Returns:
            True if removed

        Example:
            >>> removed = graph.remove_node("node_001")
        """
        if node_id in self._nodes:
            del self._nodes[node_id]
            # Remove edges involving this node
            edges_to_remove = [k for k in self._edges if node_id in k]
            for edge_key in edges_to_remove:
                del self._edges[edge_key]
            # Remove from adjacency
            if node_id in self._adjacency:
                del self._adjacency[node_id]
            # Remove from other nodes' adjacency lists
            for adj_list in self._adjacency.values():
                self._adjacency[node_id] = [(t, d) for t, d in adj_list if t != node_id]
            return True
        return False

    def remove_edge(self, source: str, target: str) -> bool:
        """Remove an edge from the graph.

        Args:
            source: Source node
            target: Target node

        Returns:
            True if removed

        Example:
            >>> removed = graph.remove_edge("node_001", "node_002")
        """
        edge_key = (source, target)
        if edge_key in self._edges:
            del self._edges[edge_key]
            # Remove from adjacency
            if source in self._adjacency:
                self._adjacency[source] = [(t, d) for t, d in self._adjacency[source] if t != target]
            return True
        return False

    def neighbors(self, node_id: str) -> list[str]:
        """Get neighbors of a node.

        Args:
            node_id: Node ID

        Returns:
            List of neighbor node IDs

        Example:
            >>> neighbors = graph.neighbors("node_001")
        """
        if node_id in self._adjacency:
            return [target for target, _ in self._adjacency[node_id]]
        return []

    def degree(self, node_id: str) -> int:
        """Get the degree of a node.

        Args:
            node_id: Node ID

        Returns:
            Node degree

        Example:
            >>> degree = graph.degree("node_001")
        """
        return len(self.neighbors(node_id))

    def shortest_path(self, source: str, target: str) -> Path | None:
        """Find shortest path between nodes using BFS.

        Args:
            source: Source node
            target: Target node

        Returns:
            Path or None

        Example:
            >>> path = graph.shortest_path("node_001", "node_002")
        """
        if source not in self._nodes or target not in self._nodes:
            return None

        if source == target:
            return [source]

        from collections import deque

        queue = deque([(source, [source])])
        visited = {source}

        while queue:
            current, path = queue.popleft()

            for neighbor in self.neighbors(current):
                if neighbor == target:
                    return path + [neighbor]

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def traverse(self, start: str, max_depth: int = 3) -> list[str]:
        """Traverse the graph using BFS.

        Args:
            start: Starting node
            max_depth: Maximum traversal depth

        Returns:
            List of visited nodes

        Example:
            >>> visited = graph.traverse("node_001")
        """
        if start not in self._nodes:
            return []

        from collections import deque

        visited = set()
        queue = deque([(start, 0)])

        while queue:
            current, depth = queue.popleft()

            if current in visited or depth >= max_depth:
                continue

            visited.add(current)

            for neighbor in self.neighbors(current):
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1))

        return list(visited)

    def validate(self) -> ValidationResult:
        """Validate the graph.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = graph.validate()
        """
        errors = []

        if not self._id:
            errors.append("Graph ID cannot be empty")

        # Validate edges reference existing nodes
        for (source, target) in self._edges:
            if source not in self._nodes:
                errors.append(f"Edge references non-existent source node: {source}")

            if target not in self._nodes:
                errors.append(f"Edge references non-existent target node: {target}")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Graph definition

        Example:
            >>> data = graph.to_dict()
        """
        return {
            "id": self._id,
            "graph_type": self._graph_type.value,
            "nodes": self._nodes,
            "edges": [(s, t, d) for (s, t), d in self._edges.items()],
            "node_count": len(self._nodes),
            "edge_count": len(self._edges),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(graph)
        """
        return f"KnowledgeGraph(id={self._id}, type={self._graph_type.value}, nodes={len(self._nodes)}, edges={len(self._edges)})"


# Export
__all__ = [
    "KnowledgeGraph",
]
