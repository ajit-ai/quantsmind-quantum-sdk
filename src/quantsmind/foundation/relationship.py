"""
Relationship Module

This module provides typed connections between entities within the QuantsMind SDK.
Relationship represents typed, directed or undirected connections between entities.

Purpose
-------
Provide typed connections for entities in the Foundation package.

Scientific Meaning
------------------
Relationship represents typed connections: physical forces (gravitational, electromagnetic),
quantum entanglement, chemical bonds, biological interactions, financial correlations.

Responsibilities
----------------
- Manage relationship endpoints
- Support relationship types
- Enable relationship serialization
- Handle relationship weights
- Support relationship queries

Dependencies
------------
typing (standard library)
logging (standard library)
quantsmind.foundation.exceptions (exception hierarchy)
quantsmind.foundation.constants (constant values)
quantsmind.foundation.types (type definitions)
quantsmind.foundation.enums (enumeration types)
quantsmind.foundation.interfaces (abstract interfaces)

Future Extensions
-----------------
- Temporal relationships
- Probabilistic relationships
- Relationship composition
- Relationship optimization
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from quantsmind.foundation.constants import DEFAULT_RELATIONSHIP_TYPE
from quantsmind.foundation.enums import RelationshipType
from quantsmind.foundation.exceptions import (
    CycleError,
    InvalidRelationshipError,
    RelationshipError,
    RelationshipNotFoundError,
)
from quantsmind.foundation.interfaces import (
    Serializable,
    Validatable,
)
from quantsmind.foundation.types import (
    EntityID,
    MetadataDict,
    SerializedData,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class Relationship(Serializable, Validatable):
    """Concrete implementation of typed connections between entities.

    This class provides a flexible relationship representation with support for
    directed/undirected, weighted, and typed relationships.

    Scientific Meaning
    ------------------
    In scientific computing, relationships represent typed connections:
    physical forces (gravitational, electromagnetic), quantum entanglement,
    chemical bonds, biological interactions, financial correlations.

    Attributes:
        _id: Unique relationship identifier
        _relationship_type: Type of relationship
        _source: Source entity ID
        _target: Target entity ID
        _weight: Optional weight value
        _metadata: Additional metadata

    Example:
        >>> rel = Relationship(
        ...     relationship_type=RelationshipType.DIRECTED,
        ...     source="entity1",
        ...     target="entity2"
        ... )
        >>> print(f"Relationship: {rel.source} -> {rel.target}")
    """

    def __init__(
        self,
        relationship_type: RelationshipType = RelationshipType.DIRECTED,
        source: Optional[EntityID] = None,
        target: Optional[EntityID] = None,
        weight: Optional[float] = None,
        metadata: Optional[MetadataDict] = None,
    ) -> None:
        """Initialize a Relationship.

        Args:
            relationship_type: Type of relationship
            source: Source entity ID
            target: Target entity ID
            weight: Optional weight value
            metadata: Optional metadata dictionary

        Raises:
            InvalidRelationshipError: If endpoints are invalid

        Example:
            >>> rel = Relationship(
            ...     relationship_type=RelationshipType.DIRECTED,
            ...     source="entity1",
            ...     target="entity2"
            ... )
        """
        self._id: str = str(uuid.uuid4())
        self._relationship_type: RelationshipType = relationship_type
        self._source: Optional[EntityID] = source
        self._target: Optional[EntityID] = target
        self._weight: Optional[float] = weight
        self._metadata: MetadataDict = metadata or {}

        self._validate_endpoints()
        logger.debug(f"Created relationship: {self._source} -> {self._target}")

    def _validate_endpoints(self) -> None:
        """Validate the relationship endpoints.

        Raises:
            InvalidRelationshipError: If endpoints are invalid
        """
        if self._relationship_type.has_direction():
            if not self._source or not self._target:
                raise InvalidRelationshipError(
                    "Directed relationship requires both source and target"
                )

    @property
    def id(self) -> str:
        """Get the relationship ID.

        Returns:
            Relationship ID

        Example:
            >>> print(f"ID: {relationship.id}")
        """
        return self._id

    @property
    def relationship_type(self) -> RelationshipType:
        """Get the relationship type.

        Returns:
            Relationship type

        Example:
            >>> print(f"Type: {relationship.relationship_type}")
        """
        return self._relationship_type

    @property
    def source(self) -> Optional[EntityID]:
        """Get the source entity ID.

        Returns:
            Source entity ID or None

        Example:
            >>> print(f"Source: {relationship.source}")
        """
        return self._source

    @property
    def target(self) -> Optional[EntityID]:
        """Get the target entity ID.

        Returns:
            Target entity ID or None

        Example:
            >>> print(f"Target: {relationship.target}")
        """
        return self._target

    @property
    def weight(self) -> Optional[float]:
        """Get the relationship weight.

        Returns:
            Weight value or None

        Example:
            >>> print(f"Weight: {relationship.weight}")
        """
        return self._weight

    @property
    def metadata(self) -> MetadataDict:
        """Get the relationship metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> print(f"Metadata: {relationship.metadata}")
        """
        return self._metadata.copy()

    @property
    def is_directed(self) -> bool:
        """Check if relationship is directed.

        Returns:
            True if directed, False otherwise

        Example:
            >>> if relationship.is_directed:
            ...     print("Directed relationship")
        """
        return self._relationship_type.has_direction()

    @property
    def has_weight(self) -> bool:
        """Check if relationship has weight.

        Returns:
            True if has weight, False otherwise

        Example:
            >>> if relationship.has_weight:
            ...     print(f"Weight: {relationship.weight}")
        """
        return self._weight is not None

    def set_weight(self, weight: float) -> None:
        """Set the relationship weight.

        Args:
            weight: New weight value

        Example:
            >>> relationship.set_weight(0.5)
        """
        self._weight = weight
        logger.debug(f"Updated relationship weight: {weight}")

    def involves_entity(self, entity_id: EntityID) -> bool:
        """Check if relationship involves an entity.

        Args:
            entity_id: Entity ID to check

        Returns:
            True if entity is involved, False otherwise

        Example:
            >>> if relationship.involves_entity("entity1"):
            ...     print("Entity is involved")
        """
        return self._source == entity_id or self._target == entity_id

    # Serializable interface implementation
    def serialize(self, format: str = "json") -> bytes:
        """Serialize the relationship to bytes.

        Args:
            format: Serialization format (currently only "json" supported)

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If format is not supported

        Example:
            >>> data = relationship.serialize(format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        data = {
            "id": self._id,
            "type": self._relationship_type.value,
            "source": self._source,
            "target": self._target,
            "weight": self._weight,
            "metadata": self._metadata,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes, format: str = "json") -> "Relationship":
        """Deserialize the relationship from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format (currently only "json" supported)

        Returns:
            Deserialized Relationship instance

        Raises:
            NotImplementedError: If format is not supported
            InvalidRelationshipError: If data is invalid

        Example:
            >>> relationship = Relationship.deserialize(data, format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        try:
            obj = json.loads(data.decode("utf-8"))
            return cls(
                relationship_type=RelationshipType(obj["type"]),
                source=obj.get("source"),
                target=obj.get("target"),
                weight=obj.get("weight"),
                metadata=obj.get("metadata"),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise InvalidRelationshipError(f"Failed to deserialize relationship: {e}") from e

    def is_serializable(self) -> bool:
        """Check if the relationship is serializable.

        Returns:
            True (relationships are always serializable)

        Example:
            >>> if relationship.is_serializable():
            ...     data = relationship.serialize()
        """
        return True

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = Relationship.get_supported_formats()
        """
        return ["json"]

    # Validatable interface implementation
    def validate(self) -> ValidationResult:
        """Validate the relationship.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = relationship.validate()
        """
        errors: list[str] = []

        try:
            self._validate_endpoints()
        except InvalidRelationshipError as e:
            errors.append(str(e))

        if self._weight is not None and (self._weight < 0 or self._weight > 1):
            errors.append("Weight must be between 0 and 1")

        return (len(errors) == 0, errors)

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = relationship.validation_errors
        """
        is_valid, errors = self.validate()
        return errors if not is_valid else []

    @property
    def validation_warnings(self) -> list[str]:
        """Get validation warnings.

        Returns:
            List of warning messages (currently empty)

        Example:
            >>> warnings = relationship.validation_warnings
        """
        return []

    # Object protocol methods
    def __repr__(self) -> str:
        """Return string representation of the relationship.

        Returns:
            String representation

        Example:
            >>> repr(relationship)
        """
        return f"Relationship(type={self._relationship_type.value}, source={self._source}, target={self._target})"

    def __str__(self) -> str:
        """Return string representation of the relationship.

        Returns:
            String representation

        Example:
            >>> str(relationship)
        """
        if self.is_directed:
            return f"{self._source} -> {self._target}"
        return f"{self._source} <-> {self._target}"

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> rel1 == rel2
        """
        if not isinstance(other, Relationship):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Return hash of the relationship.

        Returns:
            Hash value

        Example:
            >>> hash(relationship)
        """
        return hash(self._id)


# Export
__all__ = ["Relationship"]
