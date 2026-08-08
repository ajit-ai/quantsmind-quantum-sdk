"""
Lineage Module

This module provides lineage definitions for the Knowledge package.

Purpose
-------
Provide lineage management and tracking.

Responsibilities
----------------
- Define lineage structure
- Support lineage operations
- Support lineage validation
- Support lineage tracing

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.knowledge.enums import ProvenanceType
from quantsmind.knowledge.exceptions import LineageError
from quantsmind.knowledge.types import (
    LineageData,
    LineageID,
    ValidationResult,
)


class Lineage:
    """Concrete implementation of lineage.

    This class provides lineage functionality for tracking data flow and transformations.

    Attributes:
        _id: Lineage ID
        _root: Root entity ID
        _nodes: Lineage nodes
        _edges: Lineage edges
        _metadata: Lineage metadata

    Example:
        >>> lineage = Lineage("lineage_001", "root_001")
        >>> lineage.add_node("node_001", {"type": "transformation"})
    """

    def __init__(
        self,
        lineage_id: LineageID,
        root: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Lineage.

        Args:
            lineage_id: Lineage ID
            root: Root entity ID
            metadata: Lineage metadata

        Example:
            >>> lineage = Lineage("lineage_001", "root_001")
        """
        if not lineage_id:
            raise LineageError("Lineage ID cannot be empty", {"lineage_id": lineage_id})

        if not root:
            raise LineageError("Root cannot be empty", {"root": root})

        self._id = lineage_id
        self._root = root
        self._nodes: Dict[str, LineageData] = {}
        self._edges: List[tuple[str, str]] = []
        self._metadata = metadata or {}

    @property
    def id(self) -> LineageID:
        """Get the lineage ID.

        Returns:
            Lineage ID

        Example:
            >>> lid = lineage.id
        """
        return self._id

    @property
    def root(self) -> str:
        """Get the root entity ID.

        Returns:
            Root entity ID

        Example:
            >>> root = lineage.root
        """
        return self._root

    @property
    def nodes(self) -> Dict[str, LineageData]:
        """Get the lineage nodes.

        Returns:
            Nodes dictionary

        Example:
            >>> nodes = lineage.nodes
        """
        return self._nodes.copy()

    @property
    def edges(self) -> List[tuple[str, str]]:
        """Get the lineage edges.

        Returns:
            Edges list

        Example:
            >>> edges = lineage.edges
        """
        return self._edges.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the lineage metadata.

        Returns:
            Lineage metadata

        Example:
            >>> metadata = lineage.metadata
        """
        return self._metadata.copy()

    def add_node(self, node_id: str, data: Optional[LineageData] = None) -> None:
        """Add a node to the lineage.

        Args:
            node_id: Node ID
            data: Node data

        Example:
            >>> lineage.add_node("node_001", {"type": "transformation"})
        """
        if not node_id:
            raise LineageError("Node ID cannot be empty", {"node_id": node_id})

        self._nodes[node_id] = data or {}

    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the lineage.

        Args:
            node_id: Node ID

        Returns:
            True if removed

        Example:
            >>> removed = lineage.remove_node("node_001")
        """
        if node_id in self._nodes:
            del self._nodes[node_id]
            # Remove edges involving this node
            self._edges = [(s, t) for s, t in self._edges if s != node_id and t != node_id]
            return True
        return False

    def add_edge(self, source: str, target: str) -> None:
        """Add an edge to the lineage.

        Args:
            source: Source node ID
            target: Target node ID

        Example:
            >>> lineage.add_edge("node_001", "node_002")
        """
        if source not in self._nodes:
            raise LineageError("Source node not found", {"source": source})

        if target not in self._nodes:
            raise LineageError("Target node not found", {"target": target})

        self._edges.append((source, target))

    def remove_edge(self, source: str, target: str) -> bool:
        """Remove an edge from the lineage.

        Args:
            source: Source node ID
            target: Target node ID

        Returns:
            True if removed

        Example:
            >>> removed = lineage.remove_edge("node_001", "node_002")
        """
        if (source, target) in self._edges:
            self._edges.remove((source, target))
            return True
        return False

    def get_ancestors(self, node_id: str) -> List[str]:
        """Get ancestors of a node.

        Args:
            node_id: Node ID

        Returns:
            List of ancestor node IDs

        Example:
            >>> ancestors = lineage.get_ancestors("node_001")
        """
        ancestors = []
        visited = set()
        queue = [node_id]

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            for source, target in self._edges:
                if target == current and source not in visited:
                    ancestors.append(source)
                    queue.append(source)

        return ancestors

    def get_descendants(self, node_id: str) -> List[str]:
        """Get descendants of a node.

        Args:
            node_id: Node ID

        Returns:
            List of descendant node IDs

        Example:
            >>> descendants = lineage.get_descendants("node_001")
        """
        descendants = []
        visited = set()
        queue = [node_id]

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            for source, target in self._edges:
                if source == current and target not in visited:
                    descendants.append(target)
                    queue.append(target)

        return descendants

    def get_path(self, source: str, target: str) -> Optional[List[str]]:
        """Get the path between two nodes.

        Args:
            source: Source node ID
            target: Target node ID

        Returns:
            Path or None

        Example:
            >>> path = lineage.get_path("node_001", "node_002")
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

            for s, t in self._edges:
                if s == current and t not in visited:
                    if t == target:
                        return path + [target]
                    visited.add(t)
                    queue.append((t, path + [t]))

        return None

    def trace_to_root(self, node_id: str) -> List[str]:
        """Trace a node to the root.

        Args:
            node_id: Node ID

        Returns:
            Path to root

        Example:
            >>> path = lineage.trace_to_root("node_001")
        """
        return self.get_path(node_id, self._root)

    def validate(self) -> ValidationResult:
        """Validate the lineage.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = lineage.validate()
        """
        errors = []

        if not self._id:
            errors.append("Lineage ID cannot be empty")

        if not self._root:
            errors.append("Root cannot be empty")

        if self._root not in self._nodes:
            errors.append("Root node not found in nodes")

        # Validate edges reference existing nodes
        for source, target in self._edges:
            if source not in self._nodes:
                errors.append(f"Edge references non-existent source node: {source}")

            if target not in self._nodes:
                errors.append(f"Edge references non-existent target node: {target}")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Lineage definition

        Example:
            >>> data = lineage.to_dict()
        """
        return {
            "id": self._id,
            "root": self._root,
            "nodes": self._nodes,
            "edges": self._edges,
            "node_count": len(self._nodes),
            "edge_count": len(self._edges),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(lineage)
        """
        return f"Lineage(id={self._id}, root={self._root}, nodes={len(self._nodes)}, edges={len(self._edges)})"


# Export
__all__ = [
    "Lineage",
]
