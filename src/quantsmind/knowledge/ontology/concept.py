"""
Concept Module

This module provides concept definitions for the Knowledge package.

Purpose
-------
Provide concept management for ontologies.

Responsibilities
----------------
- Define concept structure
- Support concept operations
- Support concept validation
- Support concept relationships

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
from quantsmind.knowledge.types import ConceptID, ConceptName, ValidationResult


class Concept:
    """Concrete implementation of a concept.

    This class provides concept functionality.

    Attributes:
        _id: Concept ID
        _name: Concept name
        _description: Concept description
        _properties: Concept properties
        _aliases: Concept aliases
        _metadata: Concept metadata

    Example:
        >>> concept = Concept("concept_001", "Entity")
        >>> concept.name
    """

    def __init__(
        self,
        concept_id: ConceptID,
        name: ConceptName,
        description: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        aliases: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Concept.

        Args:
            concept_id: Concept ID
            name: Concept name
            description: Concept description
            properties: Concept properties
            aliases: Concept aliases
            metadata: Concept metadata

        Example:
            >>> concept = Concept("concept_001", "Entity")
        """
        if not concept_id:
            raise OntologyError("Concept ID cannot be empty")

        if not name:
            raise OntologyError("Concept name cannot be empty")

        self._id = concept_id
        self._name = name
        self._description = description
        self._properties = properties or {}
        self._aliases = aliases or []
        self._metadata = metadata or {}

    @property
    def id(self) -> ConceptID:
        """Get the concept ID.

        Returns:
            Concept ID

        Example:
            >>> cid = concept.id
        """
        return self._id

    @property
    def name(self) -> ConceptName:
        """Get the concept name.

        Returns:
            Concept name

        Example:
            >>> name = concept.name
        """
        return self._name

    @property
    def description(self) -> Optional[str]:
        """Get the concept description.

        Returns:
            Concept description

        Example:
            >>> description = concept.description
        """
        return self._description

    @property
    def properties(self) -> Dict[str, Any]:
        """Get the concept properties.

        Returns:
            Concept properties

        Example:
            >>> properties = concept.properties
        """
        return self._properties.copy()

    @property
    def aliases(self) -> List[str]:
        """Get the concept aliases.

        Returns:
            Concept aliases

        Example:
            >>> aliases = concept.aliases
        """
        return self._aliases.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the concept metadata.

        Returns:
            Concept metadata

        Example:
            >>> metadata = concept.metadata
        """
        return self._metadata.copy()

    def set_property(self, key: str, value: Any) -> None:
        """Set a concept property.

        Args:
            key: Property key
            value: Property value

        Example:
            >>> concept.set_property("color", "red")
        """
        self._properties[key] = value

    def remove_property(self, key: str) -> bool:
        """Remove a concept property.

        Args:
            key: Property key

        Returns:
            True if removed

        Example:
            >>> removed = concept.remove_property("color")
        """
        if key in self._properties:
            del self._properties[key]
            return True
        return False

    def add_alias(self, alias: str) -> None:
        """Add an alias to the concept.

        Args:
            alias: Alias to add

        Example:
            >>> concept.add_alias("entity")
        """
        if alias not in self._aliases:
            self._aliases.append(alias)

    def remove_alias(self, alias: str) -> bool:
        """Remove an alias from the concept.

        Args:
            alias: Alias to remove

        Returns:
            True if removed

        Example:
            >>> removed = concept.remove_alias("entity")
        """
        if alias in self._aliases:
            self._aliases.remove(alias)
            return True
        return False

    def validate(self) -> ValidationResult:
        """Validate the concept.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = concept.validate()
        """
        errors = []

        if not self._id:
            errors.append("Concept ID cannot be empty")

        if not self._name:
            errors.append("Concept name cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Concept definition

        Example:
            >>> data = concept.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "description": self._description,
            "properties": self._properties,
            "aliases": self._aliases,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(concept)
        """
        return f"Concept(id={self._id}, name={self._name})"


# Export
__all__ = [
    "Concept",
]
