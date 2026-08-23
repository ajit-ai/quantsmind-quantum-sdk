"""
State Module

This module provides state representation for entities and systems within the QuantsMind SDK.
State represents the complete condition of an entity or system at a point in time.

Purpose
-------
Provide state representation for entities and systems in the Foundation package.

Scientific Meaning
------------------
State represents the complete condition of an entity or system at a point in time
(quantum state vector, physical state, chemical state, biological state, financial state).

Responsibilities
----------------
- Manage state data
- Support state comparison
- Enable state serialization
- Handle state history
- Support state transformations

Dependencies
------------
typing (standard library)
logging (standard library)
datetime (standard library)
quantsmind.foundation.exceptions (exception hierarchy)
quantsmind.foundation.constants (constant values)
quantsmind.foundation.types (type definitions)
quantsmind.foundation.interfaces (abstract interfaces)

Future Extensions
-----------------
- State compression and approximation
- State differential representation
- State versioning
- Distributed state consistency
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from quantsmind.foundation.constants import ERROR_INVALID_STATE
from quantsmind.foundation.exceptions import (
    InvalidStateError,
)
from quantsmind.foundation.interfaces import (
    Cloneable,
    Comparable,
    Serializable,
    Timestamped,
    Validatable,
)
from quantsmind.foundation.types import (
    ComparisonResult,
    MetadataDict,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class State(Cloneable, Comparable, Serializable, Timestamped, Validatable):
    """Concrete implementation of state representation for entities and systems.

    This class provides a flexible state representation with support for
    arbitrary data structures, versioning, and history tracking.

    Scientific Meaning
    ------------------
    In scientific computing, state represents the complete condition of a system:
    quantum state vector, physical state (position, momentum), chemical state
    (concentrations), biological state (cell state), financial state (portfolio state).

    Attributes:
        _data: State data dictionary
        _timestamp: State timestamp
        _version: State version
        _metadata: Additional metadata

    Example:
        >>> state = State(data={"position": [1.0, 2.0], "velocity": [0.5, 0.3]})
        >>> print(f"State: {state.data}")
    """

    def __init__(
        self,
        data: dict[str, Any],
        timestamp: datetime | None = None,
        metadata: MetadataDict | None = None,
    ) -> None:
        """Initialize a State.

        Args:
            data: State data dictionary
            timestamp: Optional timestamp (defaults to current time)
            metadata: Optional metadata dictionary

        Raises:
            InvalidStateError: If data is invalid

        Example:
            >>> state = State(data={"position": [1.0, 2.0], "velocity": [0.5, 0.3]})
        """
        self._data: dict[str, Any] = data or {}
        self._timestamp: datetime = timestamp or datetime.utcnow()
        self._version: int = 1
        self._metadata: MetadataDict = metadata or {}

        self._validate_data()
        logger.debug(f"Created state with {len(self._data)} fields")

    def _validate_data(self) -> None:
        """Validate the state data.

        Raises:
            InvalidStateError: If data is invalid
        """
        if not isinstance(self._data, dict):
            raise InvalidStateError(
                "State data must be a dictionary",
                error_code=ERROR_INVALID_STATE,
            )

    @property
    def data(self) -> dict[str, Any]:
        """Get the state data.

        Returns:
            State data dictionary

        Example:
            >>> print(f"State data: {state.data}")
        """
        return self._data.copy()

    @property
    def timestamp(self) -> datetime:
        """Get the state timestamp.

        Returns:
            State timestamp

        Example:
            >>> print(f"Timestamp: {state.timestamp}")
        """
        return self._timestamp

    @property
    def version(self) -> int:
        """Get the state version.

        Returns:
            State version

        Example:
            >>> print(f"Version: {state.version}")
        """
        return self._version

    @property
    def metadata(self) -> MetadataDict:
        """Get the state metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> print(f"Metadata: {state.metadata}")
        """
        return self._metadata.copy()

    @property
    def is_valid(self) -> bool:
        """Check if the state is valid.

        Returns:
            True if valid, False otherwise

        Example:
            >>> if state.is_valid:
            ...     print("State is valid")
        """
        is_valid, _ = self.validate()
        return is_valid

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the state data.

        Args:
            key: Data key
            default: Default value if key not found

        Returns:
            Data value or default

        Example:
            >>> position = state.get("position", [0.0, 0.0])
        """
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a value in the state data.

        Args:
            key: Data key
            value: Data value

        Example:
            >>> state.set("position", [1.5, 2.5])
        """
        old_value = self._data.get(key)
        self._data[key] = value
        self._version += 1
        logger.debug(f"Updated state {key}: {old_value} -> {value}")

    def update(self, data: dict[str, Any]) -> None:
        """Update the state data with a dictionary.

        Args:
            data: Dictionary of data to update

        Example:
            >>> state.update({"position": [1.5, 2.5], "velocity": [0.6, 0.4]})
        """
        self._data.update(data)
        self._version += 1
        logger.debug(f"Updated state with {len(data)} fields")

    def remove(self, key: str) -> None:
        """Remove a key from the state data.

        Args:
            key: Data key to remove

        Raises:
            KeyError: If key not found

        Example:
            >>> state.remove("velocity")
        """
        del self._data[key]
        self._version += 1
        logger.debug(f"Removed state key: {key}")

    # Cloneable interface implementation
    def clone(self, deep: bool = True) -> State:
        """Clone the state.

        Args:
            deep: Whether to perform deep copy

        Returns:
            Cloned state

        Example:
            >>> cloned_state = state.clone(deep=True)
        """
        import copy

        if deep:
            cloned_data = copy.deepcopy(self._data)
            cloned_metadata = copy.deepcopy(self._metadata)
        else:
            cloned_data = self._data.copy()
            cloned_metadata = self._metadata.copy()

        return State(
            data=cloned_data,
            timestamp=self._timestamp,
            metadata=cloned_metadata,
        )

    def is_cloneable(self) -> bool:
        """Check if the state is cloneable.

        Returns:
            True (states are always cloneable)

        Example:
            >>> if state.is_cloneable():
            ...     cloned = state.clone()
        """
        return True

    @property
    def is_deep_cloneable(self) -> bool:
        """Check if deep cloning is supported.

        Returns:
            True (deep cloning is supported)

        Example:
            >>> if state.is_deep_cloneable:
            ...     cloned = state.clone(deep=True)
        """
        return True

    # Comparable interface implementation
    def compare(self, other: Any) -> ComparisonResult:
        """Compare with another state.

        Args:
            other: Object to compare with

        Returns:
            Tuple of (are_equal, similarity_score, differences_dict)

        Raises:
            TypeError: If other is not a State

        Example:
            >>> are_equal, similarity, differences = state1.compare(state2)
        """
        if not isinstance(other, State):
            raise TypeError(f"Cannot compare State with {type(other)}")

        are_equal = self._data == other._data
        similarity = 1.0 if are_equal else 0.0

        differences: dict[str, Any] = {}
        if not are_equal:
            for key in set(self._data.keys()) | set(other._data.keys()):
                if self._data.get(key) != other._data.get(key):
                    differences[key] = (self._data.get(key), other._data.get(key))

        return (are_equal, similarity, differences)

    def equals(self, other: Any) -> bool:
        """Check equality with another state.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> if state1.equals(state2):
            ...     print("States are equal")
        """
        if not isinstance(other, State):
            return False
        return self._data == other._data

    def is_less_than(self, other: Any) -> bool:
        """Check if this state is less than another (by version).

        Args:
            other: Object to compare with

        Returns:
            True if less than, False otherwise

        Example:
            >>> if state1.is_less_than(state2):
            ...     print("state1 < state2")
        """
        if not isinstance(other, State):
            raise TypeError(f"Cannot compare State with {type(other)}")
        return self._version < other._version

    def is_greater_than(self, other: Any) -> bool:
        """Check if this state is greater than another (by version).

        Args:
            other: Object to compare with

        Returns:
            True if greater than, False otherwise

        Example:
            >>> if state1.is_greater_than(state2):
            ...     print("state1 > state2")
        """
        if not isinstance(other, State):
            raise TypeError(f"Cannot compare State with {type(other)}")
        return self._version > other._version

    @property
    def comparison_key(self) -> Any:
        """Get the comparison key.

        Returns:
            Comparison key (version)

        Example:
            >>> key = state.comparison_key
        """
        return self._version

    # Serializable interface implementation
    def serialize(self, format: str = "json") -> bytes:
        """Serialize the state to bytes.

        Args:
            format: Serialization format (currently only "json" supported)

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If format is not supported

        Example:
            >>> data = state.serialize(format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        data = {
            "data": self._data,
            "timestamp": self._timestamp.isoformat(),
            "version": self._version,
            "metadata": self._metadata,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes, format: str = "json") -> State:
        """Deserialize the state from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format (currently only "json" supported)

        Returns:
            Deserialized State instance

        Raises:
            NotImplementedError: If format is not supported
            InvalidStateError: If data is invalid

        Example:
            >>> state = State.deserialize(data, format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        try:
            obj = json.loads(data.decode("utf-8"))
            state = cls(
                data=obj["data"],
                timestamp=datetime.fromisoformat(obj["timestamp"]),
                metadata=obj.get("metadata"),
            )
            state._version = obj["version"]
            return state
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise InvalidStateError(
                f"Failed to deserialize state: {e}",
                error_code=ERROR_INVALID_STATE,
            ) from e

    def is_serializable(self) -> bool:
        """Check if the state is serializable.

        Returns:
            True (states are always serializable)

        Example:
            >>> if state.is_serializable():
            ...     data = state.serialize()
        """
        return True

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = State.get_supported_formats()
        """
        return ["json"]

    # Timestamped interface implementation
    def get_timestamp(self) -> datetime:
        """Get the timestamp.

        Returns:
            Timestamp as datetime

        Example:
            >>> timestamp = state.get_timestamp()
        """
        return self._timestamp

    def set_timestamp(self, timestamp: datetime) -> None:
        """Set the timestamp.

        Args:
            timestamp: New timestamp

        Example:
            >>> state.set_timestamp(datetime.now())
        """
        self._timestamp = timestamp
        logger.debug(f"Updated state timestamp: {timestamp}")

    # Validatable interface implementation
    def validate(self) -> ValidationResult:
        """Validate the state.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = state.validate()
        """
        errors: list[str] = []

        try:
            self._validate_data()
        except InvalidStateError as e:
            errors.append(str(e))

        return (len(errors) == 0, errors)

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = state.validation_errors
        """
        is_valid, errors = self.validate()
        return errors if not is_valid else []

    @property
    def validation_warnings(self) -> list[str]:
        """Get validation warnings.

        Returns:
            List of warning messages (currently empty)

        Example:
            >>> warnings = state.validation_warnings
        """
        return []

    # Object protocol methods
    def __repr__(self) -> str:
        """Return string representation of the state.

        Returns:
            String representation

        Example:
            >>> repr(state)
        """
        return f"State(version={self._version}, fields={len(self._data)}, timestamp={self._timestamp})"

    def __str__(self) -> str:
        """Return string representation of the state.

        Returns:
            String representation

        Example:
            >>> str(state)
        """
        return f"State(v{self._version}): {self._data}"

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> state1 == state2
        """
        if not isinstance(other, State):
            return False
        return self._data == other._data

    def __hash__(self) -> int:
        """Return hash of the state.

        Returns:
            Hash value

        Example:
            >>> hash(state)
        """
        return hash((frozenset(self._data.items()), self._version))


# Export
__all__ = ["State"]
