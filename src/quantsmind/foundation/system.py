"""
System Module

This module provides a composition of entities within the QuantsMind SDK.
System represents a composition of entities and the relationships/interactions between them.

Purpose
-------
Provide a composition of entities for the Foundation package.

Scientific Meaning
------------------
System represents a composition: physical system (particles, fields), quantum system (qubits, gates),
chemical system (molecules, reactions), biological system (cells, organisms), financial system (instruments, markets).

Responsibilities
----------------
- Manage system entities
- Support system relationships
- Enable system state management
- Handle system interactions
- Support system constraints

Dependencies
------------
typing (standard library)
logging (standard library)
quantsmind.foundation.exceptions (exception hierarchy)
quantsmind.foundation.constants (constant values)
quantsmind.foundation.types (type definitions)
quantsmind.foundation.enums (enumeration types)
quantsmind.foundation.interfaces (abstract interfaces)
quantsmind.foundation.identity (identity module)
quantsmind.foundation.entity (entity module)
quantsmind.foundation.relationship (relationship module)
quantsmind.foundation.state (state module)

Future Extensions
-----------------
- System composition patterns
- System hierarchy
- Distributed system coordination
- System optimization
"""

from __future__ import annotations

import logging
from typing import Any

from quantsmind.foundation.enums import SerializationFormat, SystemType
from quantsmind.foundation.exceptions import (
    InvalidSystemError,
)
from quantsmind.foundation.identity import Identity
from quantsmind.foundation.interfaces import (
    Serializable,
    Validatable,
)
from quantsmind.foundation.relationship import Relationship
from quantsmind.foundation.state import State
from quantsmind.foundation.types import (
    EntityID,
    MetadataDict,
    SerializedData,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class System(Serializable, Validatable):
    """Concrete implementation of a composition of entities.

    This class provides a flexible system representation with support for
    entity management, relationships, and interactions.

    Scientific Meaning
    ------------------
    In scientific computing, systems represent compositions:
    physical system (particles, fields), quantum system (qubits, gates),
    chemical system (molecules, reactions), biological system (cells, organisms).

    Attributes:
        _identity: System identity
        _system_type: Type of system
        _entities: Dictionary of entities
        _relationships: List of relationships
        _state: System state
        _metadata: Additional metadata

    Example:
        >>> system = System(system_type=SystemType.PHYSICAL)
        >>> print(f"System ID: {system.identity.id}")
    """

    def __init__(
        self,
        system_type: SystemType = SystemType.GENERIC,
        identity: Identity | None = None,
        entities: dict[EntityID, Any] | None = None,
        relationships: list[Relationship] | None = None,
        state: State | None = None,
        metadata: MetadataDict | None = None,
    ) -> None:
        """Initialize a System.

        Args:
            system_type: Type of system
            identity: Optional identity (defaults to new Identity)
            entities: Optional dictionary of entities
            relationships: Optional list of relationships
            state: Optional system state
            metadata: Optional metadata dictionary

        Example:
            >>> system = System(system_type=SystemType.PHYSICAL)
        """
        self._identity: Identity = identity or Identity()
        self._system_type: SystemType = system_type
        self._entities: dict[EntityID, Any] = entities or {}
        self._relationships: list[Relationship] = relationships or []
        self._state: State | None = state
        self._metadata: MetadataDict = metadata or {}

        logger.debug(f"Created system: {self._identity.id} of type {system_type.value}")

    @property
    def identity(self) -> Identity:
        """Get the system identity.

        Returns:
            System identity

        Example:
            >>> print(f"System ID: {system.identity.id}")
        """
        return self._identity

    @property
    def system_type(self) -> SystemType:
        """Get the system type.

        Returns:
            System type

        Example:
            >>> print(f"Type: {system.system_type}")
        """
        return self._system_type

    @property
    def entities(self) -> dict[EntityID, Any]:
        """Get the system entities.

        Returns:
            Dictionary of entities

        Example:
            >>> print(f"Entities: {system.entities}")
        """
        return self._entities.copy()

    @property
    def relationships(self) -> list[Relationship]:
        """Get the system relationships.

        Returns:
            List of relationships

        Example:
            >>> print(f"Relationships: {system.relationships}")
        """
        return self._relationships.copy()

    @property
    def state(self) -> State | None:
        """Get the system state.

        Returns:
            System state or None

        Example:
            >>> print(f"State: {system.state}")
        """
        return self._state

    @property
    def metadata(self) -> MetadataDict:
        """Get the system metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> print(f"Metadata: {system.metadata}")
        """
        return self._metadata.copy()

    def add_entity(self, entity_id: EntityID, entity: Any) -> None:
        """Add an entity to the system.

        Args:
            entity_id: Entity ID
            entity: Entity instance

        Example:
            >>> system.add_entity("entity1", entity)
        """
        self._entities[entity_id] = entity
        logger.debug(f"Added entity {entity_id} to system {self._identity.id}")

    def remove_entity(self, entity_id: EntityID) -> None:
        """Remove an entity from the system.

        Args:
            entity_id: Entity ID

        Raises:
            KeyError: If entity not found

        Example:
            >>> system.remove_entity("entity1")
        """
        del self._entities[entity_id]
        logger.debug(f"Removed entity {entity_id} from system {self._identity.id}")

    def get_entity(self, entity_id: EntityID) -> Any | None:
        """Get an entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            Entity or None

        Example:
            >>> entity = system.get_entity("entity1")
        """
        return self._entities.get(entity_id)

    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship to the system.

        Args:
            relationship: Relationship instance

        Example:
            >>> system.add_relationship(relationship)
        """
        self._relationships.append(relationship)
        logger.debug(f"Added relationship to system {self._identity.id}")

    def remove_relationship(self, relationship_id: str) -> None:
        """Remove a relationship from the system.

        Args:
            relationship_id: Relationship ID

        Raises:
            ValueError: If relationship not found

        Example:
            >>> system.remove_relationship("rel_123")
        """
        for i, rel in enumerate(self._relationships):
            if rel.id == relationship_id:
                del self._relationships[i]
                logger.debug(f"Removed relationship {relationship_id} from system {self._identity.id}")
                return
        raise ValueError(f"Relationship {relationship_id} not found")

    def set_state(self, state: State) -> None:
        """Set the system state.

        Args:
            state: New state

        Example:
            >>> system.set_state(State(data={"energy": 100.0}))
        """
        self._state = state
        logger.debug(f"Updated state for system {self._identity.id}")

    # Serializable interface implementation
    def serialize(
        self, format: SerializationFormat | str = SerializationFormat.JSON
    ) -> SerializedData:
        """Serialize the system to bytes.

        Args:
            format: Serialization format (currently only "json" supported)

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If format is not supported

        Example:
            >>> data = system.serialize(format=SerializationFormat.JSON)
        """
        is_json = format is SerializationFormat.JSON or (
            isinstance(format, str) and format.lower() == "json"
        )
        if not is_json:
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        relationships_data = [r.serialize() for r in self._relationships]
        state_data = self._state.serialize() if self._state else None

        data = {
            "identity": self._identity.serialize().decode("utf-8"),
            "type": self._system_type.value,
            "entities": list(self._entities.keys()),  # Only store IDs
            "relationships": relationships_data,
            "state": state_data.decode("utf-8") if state_data else None,
            "metadata": self._metadata,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(
        cls, data: SerializedData, format: SerializationFormat | str = SerializationFormat.JSON
    ) -> System:
        """Deserialize the system from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format (currently only "json" supported)

        Returns:
            Deserialized System instance

        Raises:
            NotImplementedError: If format is not supported
            InvalidSystemError: If data is invalid

        Note:
            Entities are not fully serialized (only IDs). This method creates
            a system with entity IDs that must be populated with actual entities.

        Example:
            >>> system = System.deserialize(data, format=SerializationFormat.JSON)
        """
        is_json = format is SerializationFormat.JSON or (
            isinstance(format, str) and format.lower() == "json"
        )
        if not is_json:
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        try:
            obj = json.loads(data.decode("utf-8"))
            identity = Identity.deserialize(obj["identity"].encode("utf-8"))
            state = State.deserialize(obj["state"].encode("utf-8")) if obj.get("state") else None

            relationships = []
            for rel_data in obj.get("relationships", []):
                relationships.append(Relationship.deserialize(rel_data.encode("utf-8")))

            return cls(
                system_type=SystemType(obj["type"]),
                identity=identity,
                entities={eid: None for eid in obj.get("entities", [])},  # Placeholder entities
                relationships=relationships,
                state=state,
                metadata=obj.get("metadata"),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise InvalidSystemError(f"Failed to deserialize system: {e}") from e

    def is_serializable(self) -> bool:
        """Check if the system is serializable.

        Returns:
            True (systems are always serializable)

        Example:
            >>> if system.is_serializable():
            ...     data = system.serialize()
        """
        return True

    @classmethod
    def get_supported_formats(cls) -> list[SerializationFormat]:
        """Get supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = System.get_supported_formats()
        """
        return [SerializationFormat.JSON]

    # Validatable interface implementation
    def validate(self) -> ValidationResult:
        """Validate the system.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = system.validate()
        """
        errors: list[str] = []

        if not isinstance(self._identity, Identity):
            errors.append("Identity must be an Identity instance")

        if self._state is not None and not isinstance(self._state, State):
            errors.append("State must be a State instance")

        return (len(errors) == 0, errors)

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = system.validation_errors
        """
        is_valid, errors = self.validate()
        return errors if not is_valid else []

    @property
    def validation_warnings(self) -> list[str]:
        """Get validation warnings.

        Returns:
            List of warning messages (currently empty)

        Example:
            >>> warnings = system.validation_warnings
        """
        return []

    # Object protocol methods
    def __repr__(self) -> str:
        """Return string representation of the system.

        Returns:
            String representation

        Example:
            >>> repr(system)
        """
        return f"System(id={self._identity.id}, type={self._system_type.value}, entities={len(self._entities)}, relationships={len(self._relationships)})"

    def __str__(self) -> str:
        """Return string representation of the system.

        Returns:
            String representation

        Example:
            >>> str(system)
        """
        return f"{self._system_type.value} system {self._identity.id}"

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> system1 == system2
        """
        if not isinstance(other, System):
            return False
        return self._identity == other._identity

    def __hash__(self) -> int:
        """Return hash of the system.

        Returns:
            Hash value

        Example:
            >>> hash(system)
        """
        return hash(self._identity)


# Export
__all__ = ["System"]
