"""
Entity Module

This module provides the atomic unit of the QuantsMind ontology within the SDK.
Entity represents the atomic unit with identity, properties, attributes, state, behaviour, relationships, constraints, and history.

Purpose
-------
Provide the atomic unit for the Foundation package.

Scientific Meaning
------------------
Entity represents the atomic unit: particle, quantum system, chemical species, biological organism,
financial instrument, or any other fundamental object in a domain.

Responsibilities
----------------
- Manage entity identity
- Support entity properties
- Enable entity state management
- Handle entity behaviour
- Support entity relationships
- Manage entity constraints

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
quantsmind.foundation.property (property module)
quantsmind.foundation.state (state module)
quantsmind.foundation.lifecycle (lifecycle module)

Future Extensions
-----------------
- Entity composition
- Entity inheritance
- Distributed entity management
- Entity versioning
"""

from __future__ import annotations

import logging
from typing import Any

from quantsmind.foundation.enums import EntityType
from quantsmind.foundation.exceptions import (
    InvalidEntityError,
)
from quantsmind.foundation.identity import Identity
from quantsmind.foundation.interfaces import (
    Serializable,
    Validatable,
)
from quantsmind.foundation.lifecycle import Lifecycle
from quantsmind.foundation.property import Property
from quantsmind.foundation.state import State
from quantsmind.foundation.types import (
    MetadataDict,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class Entity(Serializable, Validatable):
    """Concrete implementation of the atomic unit of the QuantsMind ontology.

    This class provides a comprehensive entity representation with support for
    identity, properties, state, lifecycle, and relationships.

    Scientific Meaning
    ------------------
    In scientific computing, entities represent atomic units:
    particle, quantum system, chemical species, biological organism,
    financial instrument, or any other fundamental object in a domain.

    Attributes:
        _identity: Entity identity
        _entity_type: Type of entity
        _properties: Dictionary of properties
        _state: Current state
        _lifecycle: Lifecycle management
        _metadata: Additional metadata

    Example:
        >>> entity = Entity(entity_type=EntityType.PHYSICAL)
        >>> print(f"Entity ID: {entity.identity.id}")
    """

    def __init__(
        self,
        entity_type: EntityType = EntityType.GENERIC,
        identity: Identity | None = None,
        properties: dict[str, Property] | None = None,
        state: State | None = None,
        lifecycle: Lifecycle | None = None,
        metadata: MetadataDict | None = None,
    ) -> None:
        """Initialize an Entity.

        Args:
            entity_type: Type of entity
            identity: Optional identity (defaults to new Identity)
            properties: Optional dictionary of properties
            state: Optional state
            lifecycle: Optional lifecycle (defaults to new Lifecycle)
            metadata: Optional metadata dictionary

        Example:
            >>> entity = Entity(entity_type=EntityType.PHYSICAL)
        """
        self._identity: Identity = identity or Identity()
        self._entity_type: EntityType = entity_type
        self._properties: dict[str, Property] = properties or {}
        self._state: State | None = state
        self._lifecycle: Lifecycle = lifecycle or Lifecycle()
        self._metadata: MetadataDict = metadata or {}

        logger.debug(f"Created entity: {self._identity.id} of type {entity_type.value}")

    @property
    def identity(self) -> Identity:
        """Get the entity identity.

        Returns:
            Entity identity

        Example:
            >>> print(f"Entity ID: {entity.identity.id}")
        """
        return self._identity

    @property
    def entity_type(self) -> EntityType:
        """Get the entity type.

        Returns:
            Entity type

        Example:
            >>> print(f"Type: {entity.entity_type}")
        """
        return self._entity_type

    @property
    def properties(self) -> dict[str, Property]:
        """Get the entity properties.

        Returns:
            Dictionary of properties

        Example:
            >>> print(f"Properties: {entity.properties}")
        """
        return self._properties.copy()

    @property
    def state(self) -> State | None:
        """Get the entity state.

        Returns:
            Entity state or None

        Example:
            >>> print(f"State: {entity.state}")
        """
        return self._state

    @property
    def lifecycle(self) -> Lifecycle:
        """Get the entity lifecycle.

        Returns:
            Entity lifecycle

        Example:
            >>> print(f"Lifecycle: {entity.lifecycle.current_stage}")
        """
        return self._lifecycle

    @property
    def metadata(self) -> MetadataDict:
        """Get the entity metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> print(f"Metadata: {entity.metadata}")
        """
        return self._metadata.copy()

    def add_property(self, name: str, property: Property) -> None:
        """Add a property to the entity.

        Args:
            name: Property name
            property: Property instance

        Example:
            >>> entity.add_property("mass", Property(name="mass", value=Attribute(5.0)))
        """
        self._properties[name] = property
        logger.debug(f"Added property {name} to entity {self._identity.id}")

    def remove_property(self, name: str) -> None:
        """Remove a property from the entity.

        Args:
            name: Property name

        Raises:
            KeyError: If property not found

        Example:
            >>> entity.remove_property("mass")
        """
        del self._properties[name]
        logger.debug(f"Removed property {name} from entity {self._identity.id}")

    def get_property(self, name: str) -> Property | None:
        """Get a property by name.

        Args:
            name: Property name

        Returns:
            Property or None

        Example:
            >>> mass = entity.get_property("mass")
        """
        return self._properties.get(name)

    def set_state(self, state: State) -> None:
        """Set the entity state.

        Args:
            state: New state

        Example:
            >>> entity.set_state(State(data={"position": [1.0, 2.0]}))
        """
        self._state = state
        logger.debug(f"Updated state for entity {self._identity.id}")

    # Serializable interface implementation
    def serialize(self, format: str = "json") -> bytes:
        """Serialize the entity to bytes.

        Args:
            format: Serialization format (currently only "json" supported)

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If format is not supported

        Example:
            >>> data = entity.serialize(format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        properties_data = {k: p.serialize() for k, p in self._properties.items()}
        state_data = self._state.serialize() if self._state else None
        lifecycle_data = self._lifecycle.serialize()

        data = {
            "identity": self._identity.serialize().decode("utf-8"),
            "type": self._entity_type.value,
            "properties": properties_data,
            "state": state_data.decode("utf-8") if state_data else None,
            "lifecycle": lifecycle_data.decode("utf-8"),
            "metadata": self._metadata,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes, format: str = "json") -> Entity:
        """Deserialize the entity from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format (currently only "json" supported)

        Returns:
            Deserialized Entity instance

        Raises:
            NotImplementedError: If format is not supported
            InvalidEntityError: If data is invalid

        Example:
            >>> entity = Entity.deserialize(data, format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        try:
            obj = json.loads(data.decode("utf-8"))
            identity = Identity.deserialize(obj["identity"].encode("utf-8"))
            lifecycle = Lifecycle.deserialize(obj["lifecycle"].encode("utf-8"))
            state = State.deserialize(obj["state"].encode("utf-8")) if obj.get("state") else None

            properties = {}
            for name, prop_data in obj.get("properties", {}).items():
                properties[name] = Property.deserialize(prop_data.encode("utf-8"))

            return cls(
                entity_type=EntityType(obj["type"]),
                identity=identity,
                properties=properties,
                state=state,
                lifecycle=lifecycle,
                metadata=obj.get("metadata"),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise InvalidEntityError(f"Failed to deserialize entity: {e}") from e

    def is_serializable(self) -> bool:
        """Check if the entity is serializable.

        Returns:
            True (entities are always serializable)

        Example:
            >>> if entity.is_serializable():
            ...     data = entity.serialize()
        """
        return True

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = Entity.get_supported_formats()
        """
        return ["json"]

    # Validatable interface implementation
    def validate(self) -> ValidationResult:
        """Validate the entity.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = entity.validate()
        """
        errors: list[str] = []

        if not isinstance(self._identity, Identity):
            errors.append("Identity must be an Identity instance")

        if not isinstance(self._lifecycle, Lifecycle):
            errors.append("Lifecycle must be a Lifecycle instance")

        if self._state is not None and not isinstance(self._state, State):
            errors.append("State must be a State instance")

        return (len(errors) == 0, errors)

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = entity.validation_errors
        """
        is_valid, errors = self.validate()
        return errors if not is_valid else []

    @property
    def validation_warnings(self) -> list[str]:
        """Get validation warnings.

        Returns:
            List of warning messages (currently empty)

        Example:
            >>> warnings = entity.validation_warnings
        """
        return []

    # Object protocol methods
    def __repr__(self) -> str:
        """Return string representation of the entity.

        Returns:
            String representation

        Example:
            >>> repr(entity)
        """
        return f"Entity(id={self._identity.id}, type={self._entity_type.value}, properties={len(self._properties)})"

    def __str__(self) -> str:
        """Return string representation of the entity.

        Returns:
            String representation

        Example:
            >>> str(entity)
        """
        return f"{self._entity_type.value} entity {self._identity.id}"

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> entity1 == entity2
        """
        if not isinstance(other, Entity):
            return False
        return self._identity == other._identity

    def __hash__(self) -> int:
        """Return hash of the entity.

        Returns:
            Hash value

        Example:
            >>> hash(entity)
        """
        return hash(self._identity)


# Export
__all__ = ["Entity"]
