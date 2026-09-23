"""
Interaction Module

This module provides events through which entities exchange influence within the QuantsMind SDK.
Interaction represents an event through which one or more entities exchange influence, causing state to evolve.

Purpose
-------
Provide entity interactions for the Foundation package.

Scientific Meaning
------------------
Interaction represents entity influence exchange: particle collisions, quantum gate operations,
chemical reactions, biological interactions, financial transactions.

Responsibilities
----------------
- Manage interaction participants
- Support interaction events
- Enable interaction serialization
- Handle interaction effects
- Support interaction validation

Dependencies
------------
typing (standard library)
logging (standard library)
quantsmind.foundation.exceptions (exception hierarchy)
quantsmind.foundation.constants (constant values)
quantsmind.foundation.types (type definitions)
quantsmind.foundation.enums (enumeration types)
quantsmind.foundation.interfaces (abstract interfaces)
quantsmind.foundation.event (event module)
quantsmind.foundation.identity (identity module)

Future Extensions
-----------------
- Interaction causality tracking
- Interaction composition
- Distributed interaction processing
- Interaction optimization
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from quantsmind.foundation.enums import InteractionType, SerializationFormat
from quantsmind.foundation.event import Event
from quantsmind.foundation.exceptions import (
    InvalidInteractionError,
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


class Interaction(Serializable, Validatable):
    """Concrete implementation of entity influence exchange events.

    This class provides a flexible interaction representation with support for
    participant management, event tracking, and effect recording.

    Scientific Meaning
    ------------------
    In scientific computing, interactions represent entity influence exchange:
    particle collisions, quantum gate operations, chemical reactions,
    biological interactions, financial transactions.

    Attributes:
        _id: Unique interaction identifier
        _interaction_type: Type of interaction
        _participants: List of participant entity IDs
        _event: Associated event
        _effects: Interaction effects
        _metadata: Additional metadata

    Example:
        >>> interaction = Interaction(interaction_type=InteractionType.COLLISION)
        >>> print(f"Interaction: {interaction.interaction_type}")
    """

    def __init__(
        self,
        interaction_type: InteractionType = InteractionType.GENERIC,
        participants: list[EntityID] | None = None,
        event: Event | None = None,
        effects: dict[str, Any] | None = None,
        metadata: MetadataDict | None = None,
    ) -> None:
        """Initialize an Interaction.

        Args:
            interaction_type: Type of interaction
            participants: List of participant entity IDs
            event: Associated event
            effects: Interaction effects dictionary
            metadata: Optional metadata dictionary

        Example:
            >>> interaction = Interaction(interaction_type=InteractionType.COLLISION)
        """
        self._id: str = str(uuid.uuid4())
        self._interaction_type: InteractionType = interaction_type
        self._participants: list[EntityID] = participants or []
        self._event: Event | None = event
        self._effects: dict[str, Any] = effects or {}
        self._metadata: MetadataDict = metadata or {}

        logger.debug(f"Created interaction: {interaction_type.value}")

    @property
    def id(self) -> str:
        """Get the interaction ID.

        Returns:
            Interaction ID

        Example:
            >>> print(f"ID: {interaction.id}")
        """
        return self._id

    @property
    def interaction_type(self) -> InteractionType:
        """Get the interaction type.

        Returns:
            Interaction type

        Example:
            >>> print(f"Type: {interaction.interaction_type}")
        """
        return self._interaction_type

    @property
    def participants(self) -> list[EntityID]:
        """Get the participant entity IDs.

        Returns:
            List of participant IDs

        Example:
            >>> print(f"Participants: {interaction.participants}")
        """
        return self._participants.copy()

    @property
    def event(self) -> Event | None:
        """Get the associated event.

        Returns:
            Event or None

        Example:
            >>> print(f"Event: {interaction.event}")
        """
        return self._event

    @property
    def effects(self) -> dict[str, Any]:
        """Get the interaction effects.

        Returns:
            Effects dictionary

        Example:
            >>> print(f"Effects: {interaction.effects}")
        """
        return self._effects.copy()

    @property
    def metadata(self) -> MetadataDict:
        """Get the interaction metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> print(f"Metadata: {interaction.metadata}")
        """
        return self._metadata.copy()

    @property
    def has_event(self) -> bool:
        """Check if interaction has an associated event.

        Returns:
            True if has event, False otherwise

        Example:
            >>> if interaction.has_event:
            ...     print(f"Event: {interaction.event}")
        """
        return self._event is not None

    def add_participant(self, entity_id: EntityID) -> None:
        """Add a participant to the interaction.

        Args:
            entity_id: Entity ID

        Example:
            >>> interaction.add_participant("entity1")
        """
        if entity_id not in self._participants:
            self._participants.append(entity_id)
            logger.debug(f"Added participant {entity_id} to interaction {self._id}")

    def remove_participant(self, entity_id: EntityID) -> None:
        """Remove a participant from the interaction.

        Args:
            entity_id: Entity ID

        Raises:
            ValueError: If participant not found

        Example:
            >>> interaction.remove_participant("entity1")
        """
        if entity_id in self._participants:
            self._participants.remove(entity_id)
            logger.debug(f"Removed participant {entity_id} from interaction {self._id}")
        else:
            raise ValueError(f"Participant {entity_id} not found")

    def set_event(self, event: Event) -> None:
        """Set the associated event.

        Args:
            event: Event instance

        Example:
            >>> interaction.set_event(event)
        """
        self._event = event
        logger.debug(f"Set event for interaction {self._id}")

    def set_effect(self, key: str, value: Any) -> None:
        """Set an interaction effect.

        Args:
            key: Effect key
            value: Effect value

        Example:
            >>> interaction.set_effect("energy_transfer", 10.0)
        """
        self._effects[key] = value
        logger.debug(f"Set effect {key} for interaction {self._id}")

    # Serializable interface implementation
    def serialize(
        self, format: SerializationFormat | str = SerializationFormat.JSON
    ) -> SerializedData:
        """Serialize the interaction to bytes.

        Args:
            format: Serialization format (currently only "json" supported)

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If format is not supported

        Example:
            >>> data = interaction.serialize(format=SerializationFormat.JSON)
        """
        is_json = format is SerializationFormat.JSON or (
            isinstance(format, str) and format.lower() == "json"
        )
        if not is_json:
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        event_data = self._event.serialize() if self._event else None

        data = {
            "id": self._id,
            "type": self._interaction_type.value,
            "participants": self._participants,
            "event": event_data.decode("utf-8") if event_data else None,
            "effects": self._effects,
            "metadata": self._metadata,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(
        cls, data: SerializedData, format: SerializationFormat | str = SerializationFormat.JSON
    ) -> Interaction:
        """Deserialize the interaction from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format (currently only "json" supported)

        Returns:
            Deserialized Interaction instance

        Raises:
            NotImplementedError: If format is not supported
            InvalidInteractionError: If data is invalid

        Example:
            >>> interaction = Interaction.deserialize(data, format=SerializationFormat.JSON)
        """
        is_json = format is SerializationFormat.JSON or (
            isinstance(format, str) and format.lower() == "json"
        )
        if not is_json:
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        try:
            obj = json.loads(data.decode("utf-8"))
            event = Event.deserialize(obj["event"].encode("utf-8")) if obj.get("event") else None

            return cls(
                interaction_type=InteractionType(obj["type"]),
                participants=obj.get("participants"),
                event=event,
                effects=obj.get("effects"),
                metadata=obj.get("metadata"),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise InvalidInteractionError(f"Failed to deserialize interaction: {e}") from e

    def is_serializable(self) -> bool:
        """Check if the interaction is serializable.

        Returns:
            True (interactions are always serializable)

        Example:
            >>> if interaction.is_serializable():
            ...     data = interaction.serialize()
        """
        return True

    @classmethod
    def get_supported_formats(cls) -> list[SerializationFormat]:
        """Get supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = Interaction.get_supported_formats()
        """
        return [SerializationFormat.JSON]

    # Validatable interface implementation
    def validate(self) -> ValidationResult:
        """Validate the interaction.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = interaction.validate()
        """
        errors: list[str] = []

        if not isinstance(self._interaction_type, InteractionType):
            errors.append("Interaction type must be an InteractionType")

        if self._event is not None and not isinstance(self._event, Event):
            errors.append("Event must be an Event instance")

        return (len(errors) == 0, errors)

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = interaction.validation_errors
        """
        is_valid, errors = self.validate()
        return errors if not is_valid else []

    @property
    def validation_warnings(self) -> list[str]:
        """Get validation warnings.

        Returns:
            List of warning messages (currently empty)

        Example:
            >>> warnings = interaction.validation_warnings
        """
        return []

    # Object protocol methods
    def __repr__(self) -> str:
        """Return string representation of the interaction.

        Returns:
            String representation

        Example:
            >>> repr(interaction)
        """
        return f"Interaction(type={self._interaction_type.value}, participants={len(self._participants)})"

    def __str__(self) -> str:
        """Return string representation of the interaction.

        Returns:
            String representation

        Example:
            >>> str(interaction)
        """
        return f"{self._interaction_type.value} interaction {self._id}"

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> interaction1 == interaction2
        """
        if not isinstance(other, Interaction):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Return hash of the interaction.

        Returns:
            Hash value

        Example:
            >>> hash(interaction)
        """
        return hash(self._id)


# Export
__all__ = ["Interaction"]
