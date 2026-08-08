"""
Relationship Graph Module

This module provides relationship graph definitions for the Knowledge package.

Purpose
-------
Provide relationship graph management for representing relationships between entities.

Responsibilities
----------------
- Define relationship graph structure
- Support relationship operations
- Support relationship types
- Support relationship validation

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.graph.knowledge_graph (knowledge_graph)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.knowledge.enums import GraphType
from quantsmind.knowledge.exceptions import GraphError
from quantsmind.knowledge.graph.knowledge_graph import KnowledgeGraph
from quantsmind.knowledge.types import (
    EdgeData,
    GraphID,
    NodeData,
    ValidationResult,
)


class RelationshipGraph(KnowledgeGraph):
    """Concrete implementation of a relationship graph.

    This class provides relationship graph functionality for representing relationships between entities.

    Attributes:
        _relationship_types: Relationship type definitions
        _bidirectional: Whether relationships are bidirectional

    Example:
        >>> graph = RelationshipGraph("rel_graph_001")
        >>> graph.add_relationship("entity_001", "entity_002", "knows")
    """

    def __init__(
        self,
        graph_id: GraphID,
        bidirectional: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a RelationshipGraph.

        Args:
            graph_id: Graph ID
            bidirectional: Whether relationships are bidirectional
            metadata: Graph metadata

        Example:
            >>> graph = RelationshipGraph("rel_graph_001")
        """
        super().__init__(graph_id, GraphType.RELATIONSHIP, metadata)
        self._relationship_types: Dict[str, Dict[str, Any]] = {}
        self._bidirectional = bidirectional

    @property
    def relationship_types(self) -> Dict[str, Dict[str, Any]]:
        """Get the relationship types.

        Returns:
            Relationship type definitions

        Example:
            >>> rel_types = graph.relationship_types
        """
        return self._relationship_types.copy()

    @property
    def bidirectional(self) -> bool:
        """Get whether relationships are bidirectional.

        Returns:
            True if bidirectional

        Example:
            >>> bidirectional = graph.bidirectional
        """
        return self._bidirectional

    def add_relationship_type(self, rel_type: str, description: Optional[str] = None, properties: Optional[Dict[str, Any]] = None) -> None:
        """Add a relationship type definition.

        Args:
            rel_type: Relationship type
            description: Type description
            properties: Type properties

        Example:
            >>> graph.add_relationship_type("knows", "Acquaintance relationship")
        """
        self._relationship_types[rel_type] = {
            "description": description,
            "properties": properties or {},
        }

    def add_relationship(self, source: str, target: str, rel_type: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add a relationship to the graph.

        Args:
            source: Source node ID
            target: Target node ID
            rel_type: Relationship type
            attributes: Relationship attributes

        Example:
            >>> graph.add_relationship("entity_001", "entity_002", "knows")
        """
        if source not in self._nodes:
            raise GraphError("Source node not found", {"source": source})

        if target not in self._nodes:
            raise GraphError("Target node not found", {"target": target})

        edge_data = {"relationship_type": rel_type, **(attributes or {})}
        self.add_edge(source, target, edge_data)

        if self._bidirectional:
            self.add_edge(target, source, edge_data)

    def remove_relationship(self, source: str, target: str, rel_type: Optional[str] = None) -> bool:
        """Remove a relationship from the graph.

        Args:
            source: Source node ID
            target: Target node ID
            rel_type: Relationship type (optional)

        Returns:
            True if removed

        Example:
            >>> removed = graph.remove_relationship("entity_001", "entity_002")
        """
        removed = False

        if rel_type:
            edge_data = self.get_edge(source, target)
            if edge_data and edge_data.get("relationship_type") == rel_type:
                removed = self.remove_edge(source, target)
                if self._bidirectional:
                    self.remove_edge(target, source)
        else:
            removed = self.remove_edge(source, target)
            if self._bidirectional:
                self.remove_edge(target, source)

        return removed

    def get_relationships(self, node_id: str, rel_type: Optional[str] = None) -> List[tuple[str, str, Dict[str, Any]]]:
        """Get relationships for a node.

        Args:
            node_id: Node ID
            rel_type: Relationship type filter

        Returns:
            List of (target, relationship_type, attributes) tuples

        Example:
            >>> relationships = graph.get_relationships("entity_001")
        """
        relationships = []
        for neighbor in self.neighbors(node_id):
            edge_data = self.get_edge(node_id, neighbor)
            if edge_data:
                current_rel_type = edge_data.get("relationship_type")
                if rel_type is None or current_rel_type == rel_type:
                    relationships.append((neighbor, current_rel_type, edge_data))
        return relationships

    def get_relationships_by_type(self, rel_type: str) -> List[tuple[str, str]]:
        """Get all relationships of a specific type.

        Args:
            rel_type: Relationship type

        Returns:
            List of (source, target) tuples

        Example:
            >>> relationships = graph.get_relationships_by_type("knows")
        """
        relationships = []
        for (source, target), edge_data in self._edges.items():
            if edge_data.get("relationship_type") == rel_type:
                relationships.append((source, target))
        return relationships

    def get_relationship_strength(self, source: str, target: str) -> Optional[float]:
        """Get the strength of a relationship.

        Args:
            source: Source node ID
            target: Target node ID

        Returns:
            Relationship strength or None

        Example:
            >>> strength = graph.get_relationship_strength("entity_001", "entity_002")
        """
        edge_data = self.get_edge(source, target)
        if edge_data:
            return edge_data.get("strength", 1.0)
        return None

    def set_relationship_strength(self, source: str, target: str, strength: float) -> None:
        """Set the strength of a relationship.

        Args:
            source: Source node ID
            target: Target node ID
            strength: Relationship strength (0.0 to 1.0)

        Example:
            >>> graph.set_relationship_strength("entity_001", "entity_002", 0.8)
        """
        if strength < 0.0 or strength > 1.0:
            raise GraphError("Strength must be between 0.0 and 1.0", {"strength": strength})

        edge_data = self.get_edge(source, target)
        if edge_data:
            edge_data["strength"] = strength

    def get_mutual_relationships(self, node_id: str) -> List[str]:
        """Get nodes with mutual relationships.

        Args:
            node_id: Node ID

        Returns:
            List of node IDs with mutual relationships

        Example:
            >>> mutual = graph.get_mutual_relationships("entity_001")
        """
        mutual = []
        for neighbor in self.neighbors(node_id):
            if node_id in self.neighbors(neighbor):
                mutual.append(neighbor)
        return mutual

    def validate(self) -> ValidationResult:
        """Validate the relationship graph.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = graph.validate()
        """
        errors = []

        # Validate base graph
        base_valid, base_errors = super().validate()
        errors.extend(base_errors)

        # Validate relationship types
        for (source, target), edge_data in self._edges.items():
            rel_type = edge_data.get("relationship_type")
            if rel_type and rel_type not in self._relationship_types:
                errors.append(f"Unknown relationship type: {rel_type}")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Graph definition

        Example:
            >>> data = graph.to_dict()
        """
        data = super().to_dict()
        data.update({
            "relationship_types": self._relationship_types,
            "bidirectional": self._bidirectional,
        })
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(graph)
        """
        return f"RelationshipGraph(id={self._id}, relationships={len(self._edges)}, bidirectional={self._bidirectional})"


# Export
__all__ = [
    "RelationshipGraph",
]
