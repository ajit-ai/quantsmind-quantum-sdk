"""
Entity Graph Module

This module provides entity graph definitions for the Knowledge package.

Purpose
-------
Provide entity graph management for knowledge representation.

Responsibilities
----------------
- Define entity graph structure
- Support entity operations
- Support entity relationships
- Support entity validation

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


class EntityGraph(KnowledgeGraph):
    """Concrete implementation of an entity graph.

    This class provides entity graph functionality for representing entities and their relationships.

    Attributes:
        _entity_types: Entity type mapping
        _entity_attributes: Entity attribute mapping

    Example:
        >>> graph = EntityGraph("entity_graph_001")
        >>> graph.add_entity("entity_001", "Person", {"name": "John"})
    """

    def __init__(
        self,
        graph_id: GraphID,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an EntityGraph.

        Args:
            graph_id: Graph ID
            metadata: Graph metadata

        Example:
            >>> graph = EntityGraph("entity_graph_001")
        """
        super().__init__(graph_id, GraphType.ENTITY, metadata)
        self._entity_types: Dict[str, str] = {}
        self._entity_attributes: Dict[str, Dict[str, Any]] = {}

    @property
    def entity_types(self) -> Dict[str, str]:
        """Get the entity types.

        Returns:
            Entity type mapping

        Example:
            >>> entity_types = graph.entity_types
        """
        return self._entity_types.copy()

    @property
    def entity_attributes(self) -> Dict[str, Dict[str, Any]]:
        """Get the entity attributes.

        Returns:
            Entity attribute mapping

        Example:
            >>> attributes = graph.entity_attributes
        """
        return self._entity_attributes.copy()

    def add_entity(self, entity_id: str, entity_type: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add an entity to the graph.

        Args:
            entity_id: Entity ID
            entity_type: Entity type
            attributes: Entity attributes

        Example:
            >>> graph.add_entity("entity_001", "Person", {"name": "John"})
        """
        if not entity_id:
            raise GraphError("Entity ID cannot be empty", {"entity_id": entity_id})

        if not entity_type:
            raise GraphError("Entity type cannot be empty", {"entity_type": entity_type})

        self._entity_types[entity_id] = entity_type
        self._entity_attributes[entity_id] = attributes or {}
        self.add_node(entity_id, {"type": entity_type, **attributes})

    def remove_entity(self, entity_id: str) -> bool:
        """Remove an entity from the graph.

        Args:
            entity_id: Entity ID

        Returns:
            True if removed

        Example:
            >>> removed = graph.remove_entity("entity_001")
        """
        if entity_id in self._entity_types:
            del self._entity_types[entity_id]
            del self._entity_attributes[entity_id]
            return self.remove_node(entity_id)
        return False

    def get_entity_type(self, entity_id: str) -> Optional[str]:
        """Get the type of an entity.

        Args:
            entity_id: Entity ID

        Returns:
            Entity type or None

        Example:
            >>> entity_type = graph.get_entity_type("entity_001")
        """
        return self._entity_types.get(entity_id)

    def get_entity_attributes(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get the attributes of an entity.

        Args:
            entity_id: Entity ID

        Returns:
            Entity attributes or None

        Example:
            >>> attributes = graph.get_entity_attributes("entity_001")
        """
        return self._entity_attributes.get(entity_id)

    def get_entities_by_type(self, entity_type: str) -> List[str]:
        """Get entities by type.

        Args:
            entity_type: Entity type

        Returns:
            List of entity IDs

        Example:
            >>> entities = graph.get_entities_by_type("Person")
        """
        return [eid for eid, etype in self._entity_types.items() if etype == entity_type]

    def add_relationship(self, source: str, target: str, relationship_type: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add a relationship between entities.

        Args:
            source: Source entity ID
            target: Target entity ID
            relationship_type: Relationship type
            attributes: Relationship attributes

        Example:
            >>> graph.add_relationship("entity_001", "entity_002", "knows")
        """
        if source not in self._entity_types:
            raise GraphError("Source entity not found", {"source": source})

        if target not in self._entity_types:
            raise GraphError("Target entity not found", {"target": target})

        edge_data = {"relationship_type": relationship_type, **(attributes or {})}
        self.add_edge(source, target, edge_data)

    def get_relationships(self, entity_id: str) -> List[tuple[str, str, Dict[str, Any]]]:
        """Get relationships for an entity.

        Args:
            entity_id: Entity ID

        Returns:
            List of (target, relationship_type, attributes) tuples

        Example:
            >>> relationships = graph.get_relationships("entity_001")
        """
        relationships = []
        for neighbor in self.neighbors(entity_id):
            edge_data = self.get_edge(entity_id, neighbor)
            if edge_data:
                relationship_type = edge_data.get("relationship_type", "related")
                relationships.append((neighbor, relationship_type, edge_data))
        return relationships

    def get_relationships_by_type(self, relationship_type: str) -> List[tuple[str, str]]:
        """Get relationships by type.

        Args:
            relationship_type: Relationship type

        Returns:
            List of (source, target) tuples

        Example:
            >>> relationships = graph.get_relationships_by_type("knows")
        """
        relationships = []
        for (source, target), edge_data in self._edges.items():
            if edge_data.get("relationship_type") == relationship_type:
                relationships.append((source, target))
        return relationships

    def validate(self) -> ValidationResult:
        """Validate the entity graph.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = graph.validate()
        """
        errors = []

        # Validate base graph
        base_valid, base_errors = super().validate()
        errors.extend(base_errors)

        # Validate entity types
        for entity_id, entity_type in self._entity_types.items():
            if entity_id not in self._nodes:
                errors.append(f"Entity type references non-existent node: {entity_id}")

        # Validate entity attributes
        for entity_id, attributes in self._entity_attributes.items():
            if entity_id not in self._nodes:
                errors.append(f"Entity attributes reference non-existent node: {entity_id}")

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
            "entity_types": self._entity_types,
            "entity_attributes": self._entity_attributes,
        })
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(graph)
        """
        return f"EntityGraph(id={self._id}, entities={len(self._entity_types)}, relationships={len(self._edges)})"


# Export
__all__ = [
    "EntityGraph",
]
