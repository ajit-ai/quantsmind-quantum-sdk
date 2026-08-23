"""
Graph Index Module

This module provides graph index definitions for the Knowledge package.

Purpose
-------
Provide graph index management for efficient graph traversal.

Responsibilities
----------------
- Define graph index structure
- Support graph index operations
- Support graph index validation
- Support graph index metadata

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.knowledge.enums import IndexType
from quantsmind.knowledge.exceptions import IndexError
from quantsmind.knowledge.types import ValidationResult


class GraphIndex:
    """Concrete implementation of a graph index.

    This class provides graph index functionality for efficient graph traversal.

    Attributes:
        _id: Index ID
        _name: Index name
        _index_type: Index type
        _adjacency_index: Adjacency index
        _reverse_adjacency_index: Reverse adjacency index
        _metadata: Index metadata

    Example:
        >>> graph_index = GraphIndex("graph_idx_001", "adjacency_index", IndexType.ADJACENCY)
        >>> graph_index.add_edge("node_001", "node_002")
    """

    def __init__(
        self,
        index_id: str,
        name: str,
        index_type: IndexType,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a GraphIndex.

        Args:
            index_id: Index ID
            name: Index name
            index_type: Index type
            metadata: Index metadata

        Example:
            >>> graph_index = GraphIndex("graph_idx_001", "adjacency_index", IndexType.ADJACENCY)
        """
        if not index_id:
            raise IndexError("Index ID cannot be empty", {"index_id": index_id})

        if not name:
            raise IndexError("Index name cannot be empty", {"name": name})

        self._id = index_id
        self._name = name
        self._index_type = index_type
        self._adjacency_index: dict[str, list[str]] = {}
        self._reverse_adjacency_index: dict[str, list[str]] = {}
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the index ID.

        Returns:
            Index ID

        Example:
            >>> gid = graph_index.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the index name.

        Returns:
            Index name

        Example:
            >>> name = graph_index.name
        """
        return self._name

    @property
    def index_type(self) -> IndexType:
        """Get the index type.

        Returns:
            Index type

        Example:
            >>> itype = graph_index.index_type
        """
        return self._index_type

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the index metadata.

        Returns:
            Index metadata

        Example:
            >>> metadata = graph_index.metadata
        """
        return self._metadata.copy()

    def add_edge(self, source: str, target: str) -> None:
        """Add an edge to the graph index.

        Args:
            source: Source node
            target: Target node

        Example:
            >>> graph_index.add_edge("node_001", "node_002")
        """
        if source not in self._adjacency_index:
            self._adjacency_index[source] = []
        if target not in self._adjacency_index[source]:
            self._adjacency_index[source].append(target)

        if target not in self._reverse_adjacency_index:
            self._reverse_adjacency_index[target] = []
        if source not in self._reverse_adjacency_index[target]:
            self._reverse_adjacency_index[target].append(source)

    def remove_edge(self, source: str, target: str) -> bool:
        """Remove an edge from the graph index.

        Args:
            source: Source node
            target: Target node

        Returns:
            True if removed

        Example:
            >>> removed = graph_index.remove_edge("node_001", "node_002")
        """
        removed = False

        if source in self._adjacency_index and target in self._adjacency_index[source]:
            self._adjacency_index[source].remove(target)
            removed = True

        if target in self._reverse_adjacency_index and source in self._reverse_adjacency_index[target]:
            self._reverse_adjacency_index[target].remove(source)

        return removed

    def get_neighbors(self, node: str) -> list[str]:
        """Get neighbors of a node.

        Args:
            node: Node ID

        Returns:
            List of neighbor node IDs

        Example:
            >>> neighbors = graph_index.get_neighbors("node_001")
        """
        return self._adjacency_index.get(node, []).copy()

    def get_predecessors(self, node: str) -> list[str]:
        """Get predecessors of a node.

        Args:
            node: Node ID

        Returns:
            List of predecessor node IDs

        Example:
            >>> predecessors = graph_index.get_predecessors("node_002")
        """
        return self._reverse_adjacency_index.get(node, []).copy()

    def get_degree(self, node: str) -> int:
        """Get the degree of a node.

        Args:
            node: Node ID

        Returns:
            Node degree

        Example:
            >>> degree = graph_index.get_degree("node_001")
        """
        return len(self.get_neighbors(node))

    def get_all_nodes(self) -> list[str]:
        """Get all nodes in the index.

        Returns:
            List of node IDs

        Example:
            >>> nodes = graph_index.get_all_nodes()
        """
        nodes = set(self._adjacency_index.keys())
        nodes.update(self._reverse_adjacency_index.keys())
        return list(nodes)

    def count_nodes(self) -> int:
        """Get the number of nodes.

        Returns:
            Number of nodes

        Example:
            >>> count = graph_index.count_nodes()
        """
        return len(self.get_all_nodes())

    def count_edges(self) -> int:
        """Get the number of edges.

        Returns:
            Number of edges

        Example:
            >>> count = graph_index.count_edges()
        """
        return sum(len(neighbors) for neighbors in self._adjacency_index.values())

    def validate(self) -> ValidationResult:
        """Validate the graph index.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = graph_index.validate()
        """
        errors = []

        if not self._id:
            errors.append("Index ID cannot be empty")

        if not self._name:
            errors.append("Index name cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Index definition

        Example:
            >>> data = graph_index.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "index_type": self._index_type.value,
            "node_count": self.count_nodes(),
            "edge_count": self.count_edges(),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(graph_index)
        """
        return f"GraphIndex(id={self._id}, name={self._name}, type={self._index_type.value}, nodes={self.count_nodes()}, edges={self.count_edges()})"


# Export
__all__ = [
    "GraphIndex",
]
