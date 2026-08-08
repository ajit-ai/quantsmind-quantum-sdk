"""
Ontology Module

This module provides ontology definitions for the Knowledge package.

Purpose
-------
Provide ontology management and semantic understanding.

Responsibilities
----------------
- Define ontology structure
- Support ontology operations
- Support ontology validation
- Support ontology traversal

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.interfaces (knowledge interfaces)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.knowledge.enums import OntologyType
from quantsmind.knowledge.exceptions import OntologyError
from quantsmind.knowledge.interfaces import IOntology
from quantsmind.knowledge.types import (
    ConceptID,
    ConceptName,
    OntologyID,
    RelationID,
    RelationType,
    ValidationResult,
)


class Ontology(IOntology):
    """Concrete implementation of an ontology.

    This class provides ontology functionality.

    Attributes:
        _id: Ontology ID
        _name: Ontology name
        _ontology_type: Ontology type
        _concepts: Concepts in the ontology
        _relations: Relations in the ontology
        _metadata: Ontology metadata

    Example:
        >>> ontology = Ontology("my_ontology")
        >>> ontology.add_concept("concept_001", {"name": "Entity"})
    """

    def __init__(
        self,
        name: str,
        ontology_type: OntologyType = OntologyType.CONCEPT,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an Ontology.

        Args:
            name: Ontology name
            ontology_type: Ontology type
            metadata: Ontology metadata

        Example:
            >>> ontology = Ontology("my_ontology")
        """
        self._id: OntologyID = name
        self._name = name
        self._ontology_type = ontology_type
        self._concepts: Dict[ConceptID, Dict[str, Any]] = {}
        self._relations: List[tuple[str, RelationType, str]] = []
        self._metadata = metadata or {}

    @property
    def id(self) -> OntologyID:
        """Get the ontology ID.

        Returns:
            Ontology ID

        Example:
            >>> oid = ontology.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the ontology name.

        Returns:
            Ontology name

        Example:
            >>> name = ontology.name
        """
        return self._name

    @property
    def ontology_type(self) -> OntologyType:
        """Get the ontology type.

        Returns:
            Ontology type

        Example:
            >>> otype = ontology.ontology_type
        """
        return self._ontology_type

    @property
    def concepts(self) -> Dict[ConceptID, Dict[str, Any]]:
        """Get the concepts.

        Returns:
            Concepts dictionary

        Example:
            >>> concepts = ontology.concepts
        """
        return self._concepts.copy()

    @property
    def relations(self) -> List[tuple[str, RelationType, str]]:
        """Get the relations.

        Returns:
            Relations list

        Example:
            >>> relations = ontology.relations
        """
        return self._relations.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the ontology metadata.

        Returns:
            Ontology metadata

        Example:
            >>> metadata = ontology.metadata
        """
        return self._metadata.copy()

    def add_concept(self, concept_id: ConceptID, concept_data: Dict[str, Any]) -> None:
        """Add a concept to the ontology.

        Args:
            concept_id: Concept ID
            concept_data: Concept data

        Example:
            >>> ontology.add_concept("concept_001", {"name": "Entity"})
        """
        if not concept_id:
            raise OntologyError("Concept ID cannot be empty", {"concept_id": concept_id})

        self._concepts[concept_id] = concept_data

    def remove_concept(self, concept_id: ConceptID) -> bool:
        """Remove a concept from the ontology.

        Args:
            concept_id: Concept ID

        Returns:
            True if removed

        Example:
            >>> removed = ontology.remove_concept("concept_001")
        """
        if concept_id in self._concepts:
            del self._concepts[concept_id]
            # Remove relations involving this concept
            self._relations = [
                (s, r, t) for s, r, t in self._relations
                if s != concept_id and t != concept_id
            ]
            return True
        return False

    def get_concept(self, concept_id: ConceptID) -> Optional[Dict[str, Any]]:
        """Get a concept from the ontology.

        Args:
            concept_id: Concept ID

        Returns:
            Concept data or None

        Example:
            >>> concept = ontology.get_concept("concept_001")
        """
        return self._concepts.get(concept_id)

    def add_relation(self, source: str, relation: RelationType, target: str) -> None:
        """Add a relation to the ontology.

        Args:
            source: Source concept
            relation: Relation type
            target: Target concept

        Example:
            >>> ontology.add_relation("entity", "is_a", "physical_entity")
        """
        if source not in self._concepts:
            raise OntologyError("Source concept not found", {"source": source})

        if target not in self._concepts:
            raise OntologyError("Target concept not found", {"target": target})

        self._relations.append((source, relation, target))

    def remove_relation(self, source: str, relation: RelationType, target: str) -> bool:
        """Remove a relation from the ontology.

        Args:
            source: Source concept
            relation: Relation type
            target: Target concept

        Returns:
            True if removed

        Example:
            >>> removed = ontology.remove_relation("entity", "is_a", "physical_entity")
        """
        if (source, relation, target) in self._relations:
            self._relations.remove((source, relation, target))
            return True
        return False

    def get_relations(self, concept_id: ConceptID) -> List[tuple[RelationType, str]]:
        """Get relations for a concept.

        Args:
            concept_id: Concept ID

        Returns:
            List of (relation, target) tuples

        Example:
            >>> relations = ontology.get_relations("concept_001")
        """
        result = []
        for source, relation, target in self._relations:
            if source == concept_id:
                result.append((relation, target))
        return result

    def get_incoming_relations(self, concept_id: ConceptID) -> List[tuple[str, RelationType]]:
        """Get incoming relations for a concept.

        Args:
            concept_id: Concept ID

        Returns:
            List of (source, relation) tuples

        Example:
            >>> relations = ontology.get_incoming_relations("concept_001")
        """
        result = []
        for source, relation, target in self._relations:
            if target == concept_id:
                result.append((source, relation))
        return result

    def traverse(self, start: str, max_depth: int = 3) -> List[str]:
        """Traverse the ontology.

        Args:
            start: Starting concept
            max_depth: Maximum traversal depth

        Returns:
            List of visited concepts

        Example:
            >>> visited = ontology.traverse("concept_001")
        """
        if start not in self._concepts:
            return []

        visited = set()
        queue = [(start, 0)]

        while queue:
            current, depth = queue.pop(0)

            if current in visited or depth >= max_depth:
                continue

            visited.add(current)

            for relation, target in self.get_relations(current):
                if target not in visited:
                    queue.append((target, depth + 1))

        return list(visited)

    def get_sub_concepts(self, concept_id: ConceptID) -> List[str]:
        """Get sub-concepts (children) of a concept.

        Args:
            concept_id: Concept ID

        Returns:
            List of sub-concept IDs

        Example:
            >>> sub_concepts = ontology.get_sub_concepts("concept_001")
        """
        result = []
        for source, relation, target in self._relations:
            if relation == "is_a" and target == concept_id:
                result.append(source)
        return result

    def get_super_concepts(self, concept_id: ConceptID) -> List[str]:
        """Get super-concepts (parents) of a concept.

        Args:
            concept_id: Concept ID

        Returns:
            List of super-concept IDs

        Example:
            >>> super_concepts = ontology.get_super_concepts("concept_001")
        """
        result = []
        for source, relation, target in self._relations:
            if relation == "is_a" and source == concept_id:
                result.append(target)
        return result

    def validate(self) -> ValidationResult:
        """Validate the ontology.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = ontology.validate()
        """
        errors = []

        # Check ontology name
        if not self._name:
            errors.append("Ontology name cannot be empty")

        # Check concepts
        if not self._concepts:
            errors.append("Ontology must have at least one concept")

        # Validate relations
        for source, relation, target in self._relations:
            if source not in self._concepts:
                errors.append(f"Relation source '{source}' not found in concepts")

            if target not in self._concepts:
                errors.append(f"Relation target '{target}' not found in concepts")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Ontology definition

        Example:
            >>> data = ontology.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "ontology_type": self._ontology_type.value,
            "concepts": self._concepts,
            "relations": [(s, r, t) for s, r, t in self._relations],
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(ontology)
        """
        return f"Ontology(id={self._id}, name={self._name}, type={self._ontology_type.value}, concepts={len(self._concepts)}, relations={len(self._relations)})"


# Export
__all__ = [
    "Ontology",
]
