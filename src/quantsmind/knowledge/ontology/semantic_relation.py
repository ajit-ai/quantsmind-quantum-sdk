"""
Semantic Relation Module

This module provides semantic relation definitions for the Knowledge package.

Purpose
-------
Provide semantic relation management for ontologies.

Responsibilities
----------------
- Define semantic relation structure
- Support semantic relation operations
- Support semantic relation validation
- Support relation types

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.knowledge.enums import OntologyType
from quantsmind.knowledge.exceptions import OntologyError
from quantsmind.knowledge.types import RelationID, RelationType, ValidationResult


class SemanticRelation:
    """Concrete implementation of a semantic relation.

    This class provides semantic relation functionality.

    Attributes:
        _id: Relation ID
        _relation_type: Relation type
        _source: Source concept ID
        _target: Target concept ID
        _properties: Relation properties
        _weight: Relation weight
        _metadata: Relation metadata

    Example:
        >>> relation = SemanticRelation("rel_001", "is_a", "concept_001", "concept_002")
        >>> relation.relation_type
    """

    def __init__(
        self,
        relation_id: RelationID,
        relation_type: RelationType,
        source: str,
        target: str,
        weight: float = 1.0,
        properties: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a SemanticRelation.

        Args:
            relation_id: Relation ID
            relation_type: Relation type
            source: Source concept ID
            target: Target concept ID
            weight: Relation weight
            properties: Relation properties
            metadata: Relation metadata

        Example:
            >>> relation = SemanticRelation("rel_001", "is_a", "concept_001", "concept_002")
        """
        if not relation_id:
            raise OntologyError("Relation ID cannot be empty")

        if not relation_type:
            raise OntologyError("Relation type cannot be empty")

        if not source:
            raise OntologyError("Source cannot be empty")

        if not target:
            raise OntologyError("Target cannot be empty")

        self._id = relation_id
        self._relation_type = relation_type
        self._source = source
        self._target = target
        self._weight = weight
        self._properties = properties or {}
        self._metadata = metadata or {}

    @property
    def id(self) -> RelationID:
        """Get the relation ID.

        Returns:
            Relation ID

        Example:
            >>> rid = relation.id
        """
        return self._id

    @property
    def relation_type(self) -> RelationType:
        """Get the relation type.

        Returns:
            Relation type

        Example:
            >>> rtype = relation.relation_type
        """
        return self._relation_type

    @property
    def source(self) -> str:
        """Get the source concept ID.

        Returns:
            Source concept ID

        Example:
            >>> source = relation.source
        """
        return self._source

    @property
    def target(self) -> str:
        """Get the target concept ID.

        Returns:
            Target concept ID

        Example:
            >>> target = relation.target
        """
        return self._target

    @property
    def weight(self) -> float:
        """Get the relation weight.

        Returns:
            Relation weight

        Example:
            >>> weight = relation.weight
        """
        return self._weight

    @property
    def properties(self) -> Dict[str, Any]:
        """Get the relation properties.

        Returns:
            Relation properties

        Example:
            >>> properties = relation.properties
        """
        return self._properties.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the relation metadata.

        Returns:
            Relation metadata

        Example:
            >>> metadata = relation.metadata
        """
        return self._metadata.copy()

    def set_weight(self, weight: float) -> None:
        """Set the relation weight.

        Args:
            weight: Relation weight

        Example:
            >>> relation.set_weight(0.5)
        """
        self._weight = weight

    def set_property(self, key: str, value: Any) -> None:
        """Set a relation property.

        Args:
            key: Property key
            value: Property value

        Example:
            >>> relation.set_property("confidence", 0.9)
        """
        self._properties[key] = value

    def remove_property(self, key: str) -> bool:
        """Remove a relation property.

        Args:
            key: Property key

        Returns:
            True if removed

        Example:
            >>> removed = relation.remove_property("confidence")
        """
        if key in self._properties:
            del self._properties[key]
            return True
        return False

    def is_symmetric(self) -> bool:
        """Check if relation is symmetric.

        Returns:
            True if symmetric

        Example:
            >>> symmetric = relation.is_symmetric()
        """
        symmetric_types = ["related_to", "similar_to", "connected_to"]
        return self._relation_type in symmetric_types

    def is_transitive(self) -> bool:
        """Check if relation is transitive.

        Returns:
            True if transitive

        Example:
            >>> transitive = relation.is_transitive()
        """
        transitive_types = ["is_a", "part_of", "contained_in"]
        return self._relation_type in transitive_types

    def is_reflexive(self) -> bool:
        """Check if relation is reflexive.

        Returns:
            True if reflexive

        Example:
            >>> reflexive = relation.is_reflexive()
        """
        reflexive_types = ["same_as", "equivalent_to"]
        return self._relation_type in reflexive_types

    def validate(self) -> ValidationResult:
        """Validate the relation.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = relation.validate()
        """
        errors = []

        if not self._id:
            errors.append("Relation ID cannot be empty")

        if not self._relation_type:
            errors.append("Relation type cannot be empty")

        if not self._source:
            errors.append("Source cannot be empty")

        if not self._target:
            errors.append("Target cannot be empty")

        if self._weight < 0 or self._weight > 1:
            errors.append("Weight must be between 0 and 1")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Relation definition

        Example:
            >>> data = relation.to_dict()
        """
        return {
            "id": self._id,
            "relation_type": self._relation_type,
            "source": self._source,
            "target": self._target,
            "weight": self._weight,
            "properties": self._properties,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(relation)
        """
        return f"SemanticRelation(id={self._id}, type={self._relation_type}, source={self._source}, target={self._target})"


class RelationRegistry:
    """Registry for semantic relations.

    This class provides relation registry functionality.

    Attributes:
        _relations: Registered relations
        _relation_types: Available relation types

    Example:
        >>> registry = RelationRegistry()
        >>> registry.register(SemanticRelation("rel_001", "is_a", "c1", "c2"))
    """

    def __init__(self) -> None:
        """Initialize a RelationRegistry.

        Example:
            >>> registry = RelationRegistry()
        """
        self._relations: Dict[RelationID, SemanticRelation] = {}
        self._relation_types = {
            "is_a": "Subclass relationship",
            "part_of": "Part-whole relationship",
            "contained_in": "Spatial containment",
            "related_to": "Generic relationship",
            "similar_to": "Similarity relationship",
            "connected_to": "Connection relationship",
            "same_as": "Equivalence relationship",
            "equivalent_to": "Equivalence relationship",
            "has_property": "Property relationship",
            "causes": "Causal relationship",
            "precedes": "Temporal precedence",
            "located_at": "Spatial location",
            "has_role": "Role relationship",
        }

    def register(self, relation: SemanticRelation) -> None:
        """Register a relation.

        Args:
            relation: Relation to register

        Example:
            >>> registry.register(SemanticRelation("rel_001", "is_a", "c1", "c2"))
        """
        self._relations[relation.id] = relation

    def unregister(self, relation_id: RelationID) -> bool:
        """Unregister a relation.

        Args:
            relation_id: Relation ID

        Returns:
            True if unregistered

        Example:
            >>> unregistered = registry.unregister("rel_001")
        """
        if relation_id in self._relations:
            del self._relations[relation_id]
            return True
        return False

    def get(self, relation_id: RelationID) -> Optional[SemanticRelation]:
        """Get a relation by ID.

        Args:
            relation_id: Relation ID

        Returns:
            Relation or None

        Example:
            >>> relation = registry.get("rel_001")
        """
        return self._relations.get(relation_id)

    def get_by_type(self, relation_type: RelationType) -> List[SemanticRelation]:
        """Get relations by type.

        Args:
            relation_type: Relation type

        Returns:
            List of relations

        Example:
            >>> relations = registry.get_by_type("is_a")
        """
        return [rel for rel in self._relations.values() if rel.relation_type == relation_type]

    def get_by_source(self, source: str) -> List[SemanticRelation]:
        """Get relations by source.

        Args:
            source: Source concept ID

        Returns:
            List of relations

        Example:
            >>> relations = registry.get_by_source("concept_001")
        """
        return [rel for rel in self._relations.values() if rel.source == source]

    def get_by_target(self, target: str) -> List[SemanticRelation]:
        """Get relations by target.

        Args:
            target: Target concept ID

        Returns:
            List of relations

        Example:
            >>> relations = registry.get_by_target("concept_002")
        """
        return [rel for rel in self._relations.values() if rel.target == target]

    def get_relation_types(self) -> Dict[str, str]:
        """Get available relation types.

        Returns:
            Dictionary of relation types and descriptions

        Example:
            >>> types = registry.get_relation_types()
        """
        return self._relation_types.copy()

    def add_relation_type(self, relation_type: str, description: str) -> None:
        """Add a custom relation type.

        Args:
            relation_type: Relation type
            description: Type description

        Example:
            >>> registry.add_relation_type("custom_rel", "Custom relationship")
        """
        self._relation_types[relation_type] = description

    def list_all(self) -> List[SemanticRelation]:
        """List all registered relations.

        Returns:
            List of relations

        Example:
            >>> relations = registry.list_all()
        """
        return list(self._relations.values())

    def count(self) -> int:
        """Get the number of registered relations.

        Returns:
            Number of relations

        Example:
            >>> count = registry.count()
        """
        return len(self._relations)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Registry state

        Example:
            >>> data = registry.to_dict()
        """
        return {
            "relations": [rel.to_dict() for rel in self._relations.values()],
            "relation_types": self._relation_types,
            "count": len(self._relations),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(registry)
        """
        return f"RelationRegistry(relations={len(self._relations)}, types={len(self._relation_types)})"


# Export
__all__ = [
    "SemanticRelation",
    "RelationRegistry",
]
