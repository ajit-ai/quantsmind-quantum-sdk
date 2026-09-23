"""
Lifecycle Module

This module provides lifecycle management for entities and systems within the QuantsMind SDK.
Lifecycle represents the ordered set of stages (create, activate, evolve, deactivate, dispose).

Purpose
-------
Provide lifecycle management for entities and systems in the Foundation package.

Scientific Meaning
------------------
Lifecycle represents the ordered stages: particle creation/annihilation, quantum state preparation,
chemical reaction initiation/termination, cell birth/death, financial instrument issuance/maturity.

Responsibilities
----------------
- Manage lifecycle stages
- Support stage transitions
- Enable lifecycle serialization
- Handle lifecycle events
- Support lifecycle validation

Dependencies
------------
typing (standard library)
logging (standard library)
datetime (standard library)
quantsmind.foundation.exceptions (exception hierarchy)
quantsmind.foundation.constants (constant values)
quantsmind.foundation.types (type definitions)
quantsmind.foundation.enums (enumeration types)
quantsmind.foundation.interfaces (abstract interfaces)

Future Extensions
-----------------
- Lifecycle hooks
- Lifecycle observers
- Distributed lifecycle coordination
- Lifecycle rollback
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from quantsmind.foundation.enums import LifecycleStage, SerializationFormat
from quantsmind.foundation.exceptions import (
    InvalidLifecycleError,
    TransitionError,
)
from quantsmind.foundation.interfaces import (
    Serializable,
    Validatable,
)
from quantsmind.foundation.types import (
    MetadataDict,
    SerializedData,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class Lifecycle(Serializable, Validatable):
    """Concrete implementation of lifecycle management for entities and systems.

    This class provides a flexible lifecycle representation with support for
    stage tracking, transition validation, and event recording.

    Scientific Meaning
    ------------------
    In scientific computing, lifecycle represents ordered stages:
    particle creation/annihilation, quantum state preparation, chemical reaction
    initiation/termination, cell birth/death, financial instrument issuance/maturity.

    Attributes:
        _current_stage: Current lifecycle stage
        _stage_history: List of stage transitions
        _created_at: Creation timestamp
        _metadata: Additional metadata

    Example:
        >>> lifecycle = Lifecycle(current_stage=LifecycleStage.CREATED)
        >>> lifecycle.transition_to(LifecycleStage.ACTIVATED)
        >>> print(f"Current stage: {lifecycle.current_stage}")
    """

    def __init__(
        self,
        current_stage: LifecycleStage = LifecycleStage.CREATED,
        metadata: MetadataDict | None = None,
    ) -> None:
        """Initialize a Lifecycle.

        Args:
            current_stage: Current lifecycle stage
            metadata: Optional metadata dictionary

        Example:
            >>> lifecycle = Lifecycle(current_stage=LifecycleStage.CREATED)
        """
        self._current_stage: LifecycleStage = current_stage
        # Naive-preserving utcnow replacement (deprecated in 3.12+):
        # timezone-aware now with tzinfo stripped keeps naive semantics.
        now = datetime.now(UTC).replace(tzinfo=None)
        self._stage_history: list[tuple[LifecycleStage, datetime]] = [(current_stage, now)]
        self._created_at: datetime = now
        self._metadata: MetadataDict = metadata or {}

        logger.debug(f"Created lifecycle at stage: {current_stage.value}")

    @property
    def current_stage(self) -> LifecycleStage:
        """Get the current lifecycle stage.

        Returns:
            Current lifecycle stage

        Example:
            >>> print(f"Current stage: {lifecycle.current_stage}")
        """
        return self._current_stage

    @property
    def stage_history(self) -> list[tuple[LifecycleStage, datetime]]:
        """Get the stage history.

        Returns:
            List of (stage, timestamp) tuples

        Example:
            >>> print(f"History: {lifecycle.stage_history}")
        """
        return self._stage_history.copy()

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp.

        Returns:
            Creation timestamp

        Example:
            >>> print(f"Created at: {lifecycle.created_at}")
        """
        return self._created_at

    @property
    def metadata(self) -> MetadataDict:
        """Get the lifecycle metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> print(f"Metadata: {lifecycle.metadata}")
        """
        return self._metadata.copy()

    @property
    def is_active(self) -> bool:
        """Check if lifecycle is in an active stage.

        Returns:
            True if active, False otherwise

        Example:
            >>> if lifecycle.is_active:
            ...     print("Lifecycle is active")
        """
        return self._current_stage.is_active()

    @property
    def is_terminal(self) -> bool:
        """Check if lifecycle is in a terminal stage.

        Returns:
            True if terminal, False otherwise

        Example:
            >>> if lifecycle.is_terminal:
            ...     print("Lifecycle is terminal")
        """
        return self._current_stage.is_terminal()

    def transition_to(self, new_stage: LifecycleStage) -> None:
        """Transition to a new lifecycle stage.

        Args:
            new_stage: New lifecycle stage

        Raises:
            TransitionError: If transition is invalid

        Example:
            >>> lifecycle.transition_to(LifecycleStage.ACTIVATED)
        """
        if not self._is_valid_transition(new_stage):
            raise TransitionError(
                f"Invalid transition from {self._current_stage.value} to {new_stage.value}"
            )

        old_stage = self._current_stage
        self._current_stage = new_stage
        self._stage_history.append(
            (new_stage, datetime.now(UTC).replace(tzinfo=None))
        )
        logger.debug(f"Transitioned lifecycle: {old_stage.value} -> {new_stage.value}")

    def _is_valid_transition(self, new_stage: LifecycleStage) -> bool:
        """Validate a lifecycle transition.

        Args:
            new_stage: Target stage

        Returns:
            True if valid, False otherwise
        """
        # Terminal stages cannot transition
        if self._current_stage.is_terminal():
            return False

        # Valid transitions
        valid_transitions = {
            LifecycleStage.CREATED: [LifecycleStage.ACTIVATED, LifecycleStage.DISPOSED],
            LifecycleStage.ACTIVATED: [LifecycleStage.EVOLVING, LifecycleStage.DEACTIVATED],
            LifecycleStage.EVOLVING: [LifecycleStage.EVOLVING, LifecycleStage.DEACTIVATED],
            LifecycleStage.DEACTIVATED: [LifecycleStage.ACTIVATED, LifecycleStage.DISPOSED],
        }

        return new_stage in valid_transitions.get(self._current_stage, [])

    # Serializable interface implementation
    def serialize(
        self, format: SerializationFormat | str = SerializationFormat.JSON
    ) -> SerializedData:
        """Serialize the lifecycle to bytes.

        Args:
            format: Serialization format (currently only "json" supported)

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If format is not supported

        Example:
            >>> data = lifecycle.serialize(format="json")
        """
        is_json = format is SerializationFormat.JSON or (
            isinstance(format, str) and format.lower() == "json"
        )
        if not is_json:
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        history = [(stage.value, ts.isoformat()) for stage, ts in self._stage_history]

        data = {
            "current_stage": self._current_stage.value,
            "stage_history": history,
            "created_at": self._created_at.isoformat(),
            "metadata": self._metadata,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(
        cls, data: SerializedData, format: SerializationFormat | str = SerializationFormat.JSON
    ) -> Lifecycle:
        """Deserialize the lifecycle from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format (currently only "json" supported)

        Returns:
            Deserialized Lifecycle instance

        Raises:
            NotImplementedError: If format is not supported
            InvalidLifecycleError: If data is invalid

        Example:
            >>> lifecycle = Lifecycle.deserialize(data, format="json")
        """
        is_json = format is SerializationFormat.JSON or (
            isinstance(format, str) and format.lower() == "json"
        )
        if not is_json:
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        try:
            obj = json.loads(data.decode("utf-8"))
            lifecycle = cls(
                current_stage=LifecycleStage(obj["current_stage"]),
                metadata=obj.get("metadata"),
            )
            lifecycle._created_at = datetime.fromisoformat(obj["created_at"])
            lifecycle._stage_history = [
                (LifecycleStage(stage), datetime.fromisoformat(ts))
                for stage, ts in obj["stage_history"]
            ]
            return lifecycle
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise InvalidLifecycleError(f"Failed to deserialize lifecycle: {e}") from e

    def is_serializable(self) -> bool:
        """Check if the lifecycle is serializable.

        Returns:
            True (lifecycles are always serializable)

        Example:
            >>> if lifecycle.is_serializable():
            ...     data = lifecycle.serialize()
        """
        return True

    @classmethod
    def get_supported_formats(cls) -> list[SerializationFormat]:
        """Get supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = Lifecycle.get_supported_formats()
        """
        return [SerializationFormat.JSON]

    # Validatable interface implementation
    def validate(self) -> ValidationResult:
        """Validate the lifecycle.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = lifecycle.validate()
        """
        errors: list[str] = []

        if not isinstance(self._current_stage, LifecycleStage):
            errors.append("Current stage must be a LifecycleStage")

        return (len(errors) == 0, errors)

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = lifecycle.validation_errors
        """
        is_valid, errors = self.validate()
        return errors if not is_valid else []

    @property
    def validation_warnings(self) -> list[str]:
        """Get validation warnings.

        Returns:
            List of warning messages (currently empty)

        Example:
            >>> warnings = lifecycle.validation_warnings
        """
        return []

    # Object protocol methods
    def __repr__(self) -> str:
        """Return string representation of the lifecycle.

        Returns:
            String representation

        Example:
            >>> repr(lifecycle)
        """
        return f"Lifecycle(stage={self._current_stage.value}, transitions={len(self._stage_history)})"

    def __str__(self) -> str:
        """Return string representation of the lifecycle.

        Returns:
            String representation

        Example:
            >>> str(lifecycle)
        """
        return str(self._current_stage.value)

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> lifecycle1 == lifecycle2
        """
        if not isinstance(other, Lifecycle):
            return False
        return self._current_stage == other._current_stage

    def __hash__(self) -> int:
        """Return hash of the lifecycle.

        Returns:
            Hash value

        Example:
            >>> hash(lifecycle)
        """
        return hash(self._current_stage)


# Export
__all__ = ["Lifecycle"]
