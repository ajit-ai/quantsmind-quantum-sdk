"""
Observation Module

This module provides recorded measurements within the QuantsMind SDK.
Observation represents a recorded measurement of state at a point in space and time.

Purpose
-------
Provide recorded measurements for entities and systems in the Foundation package.

Scientific Meaning
------------------
Observation represents recorded measurements: particle detection, quantum measurement,
chemical concentration measurement, biological observation, financial market observation.

Responsibilities
----------------
- Manage observation data
- Support observation timestamps
- Enable observation serialization
- Handle observation uncertainty
- Support observation queries

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
- Observation uncertainty quantification
- Observation correlation
- Distributed observation processing
- Observation streams
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from quantsmind.foundation.constants import DEFAULT_OBSERVATION_TYPE
from quantsmind.foundation.enums import ObservationType
from quantsmind.foundation.exceptions import (
    InvalidObservationError,
    ObservationError,
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


class Observation(Serializable, Validatable):
    """Concrete implementation of recorded measurements.

    This class provides a flexible observation representation with support for
    various observation types, timestamps, and associated data.

    Scientific Meaning
    ------------------
    In scientific computing, observations represent recorded measurements:
    particle detection, quantum measurement, chemical concentration measurement,
    biological observation, financial market observation.

    Attributes:
        _id: Unique observation identifier
        _observation_type: Type of observation
        _timestamp: Observation timestamp
        _value: Observed value
        _uncertainty: Optional uncertainty value
        _metadata: Additional metadata

    Example:
        >>> obs = Observation(observation_type=ObservationType.MEASUREMENT, value=42.5)
        >>> print(f"Observation: {obs.value} at {obs.timestamp}")
    """

    def __init__(
        self,
        observation_type: ObservationType = ObservationType.MEASUREMENT,
        value: Optional[Any] = None,
        timestamp: Optional[datetime] = None,
        uncertainty: Optional[float] = None,
        metadata: Optional[MetadataDict] = None,
    ) -> None:
        """Initialize an Observation.

        Args:
            observation_type: Type of observation
            value: Observed value
            timestamp: Observation timestamp (defaults to current time)
            uncertainty: Optional uncertainty value
            metadata: Optional metadata dictionary

        Example:
            >>> obs = Observation(observation_type=ObservationType.MEASUREMENT, value=42.5)
        """
        self._id: str = str(uuid.uuid4())
        self._observation_type: ObservationType = observation_type
        self._timestamp: datetime = timestamp or datetime.utcnow()
        self._value: Optional[Any] = value
        self._uncertainty: Optional[float] = uncertainty
        self._metadata: MetadataDict = metadata or {}

        logger.debug(f"Created observation: {observation_type.value} at {self._timestamp}")

    @property
    def id(self) -> str:
        """Get the observation ID.

        Returns:
            Observation ID

        Example:
            >>> print(f"ID: {observation.id}")
        """
        return self._id

    @property
    def observation_type(self) -> ObservationType:
        """Get the observation type.

        Returns:
            Observation type

        Example:
            >>> print(f"Type: {observation.observation_type}")
        """
        return self._observation_type

    @property
    def timestamp(self) -> datetime:
        """Get the observation timestamp.

        Returns:
            Observation timestamp

        Example:
            >>> print(f"Timestamp: {observation.timestamp}")
        """
        return self._timestamp

    @property
    def value(self) -> Optional[Any]:
        """Get the observed value.

        Returns:
            Observed value or None

        Example:
            >>> print(f"Value: {observation.value}")
        """
        return self._value

    @property
    def uncertainty(self) -> Optional[float]:
        """Get the uncertainty value.

        Returns:
            Uncertainty value or None

        Example:
            >>> print(f"Uncertainty: {observation.uncertainty}")
        """
        return self._uncertainty

    @property
    def metadata(self) -> MetadataDict:
        """Get the observation metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> print(f"Metadata: {observation.metadata}")
        """
        return self._metadata.copy()

    @property
    def has_uncertainty(self) -> bool:
        """Check if observation has uncertainty.

        Returns:
            True if has uncertainty, False otherwise

        Example:
            >>> if observation.has_uncertainty:
            ...     print(f"Uncertainty: {observation.uncertainty}")
        """
        return self._uncertainty is not None

    def set_value(self, value: Any) -> None:
        """Set the observed value.

        Args:
            value: New observed value

        Example:
            >>> observation.set_value(43.0)
        """
        self._value = value
        logger.debug(f"Updated observation value: {value}")

    def set_uncertainty(self, uncertainty: float) -> None:
        """Set the uncertainty value.

        Args:
            uncertainty: New uncertainty value

        Example:
            >>> observation.set_uncertainty(0.1)
        """
        self._uncertainty = uncertainty
        logger.debug(f"Updated observation uncertainty: {uncertainty}")

    # Serializable interface implementation
    def serialize(self, format: str = "json") -> bytes:
        """Serialize the observation to bytes.

        Args:
            format: Serialization format (currently only "json" supported)

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If format is not supported

        Example:
            >>> data = observation.serialize(format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        data = {
            "id": self._id,
            "type": self._observation_type.value,
            "timestamp": self._timestamp.isoformat(),
            "value": self._value,
            "uncertainty": self._uncertainty,
            "metadata": self._metadata,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes, format: str = "json") -> "Observation":
        """Deserialize the observation from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format (currently only "json" supported)

        Returns:
            Deserialized Observation instance

        Raises:
            NotImplementedError: If format is not supported
            InvalidObservationError: If data is invalid

        Example:
            >>> observation = Observation.deserialize(data, format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        try:
            obj = json.loads(data.decode("utf-8"))
            return cls(
                observation_type=ObservationType(obj["type"]),
                value=obj.get("value"),
                timestamp=datetime.fromisoformat(obj["timestamp"]),
                uncertainty=obj.get("uncertainty"),
                metadata=obj.get("metadata"),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise InvalidObservationError(f"Failed to deserialize observation: {e}") from e

    def is_serializable(self) -> bool:
        """Check if the observation is serializable.

        Returns:
            True (observations are always serializable)

        Example:
            >>> if observation.is_serializable():
            ...     data = observation.serialize()
        """
        return True

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = Observation.get_supported_formats()
        """
        return ["json"]

    # Validatable interface implementation
    def validate(self) -> ValidationResult:
        """Validate the observation.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = observation.validate()
        """
        errors: list[str] = []

        if not isinstance(self._observation_type, ObservationType):
            errors.append("Observation type must be an ObservationType")

        if self._uncertainty is not None and self._uncertainty < 0:
            errors.append("Uncertainty must be non-negative")

        return (len(errors) == 0, errors)

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = observation.validation_errors
        """
        is_valid, errors = self.validate()
        return errors if not is_valid else []

    @property
    def validation_warnings(self) -> list[str]:
        """Get validation warnings.

        Returns:
            List of warning messages (currently empty)

        Example:
            >>> warnings = observation.validation_warnings
        """
        return []

    # Object protocol methods
    def __repr__(self) -> str:
        """Return string representation of the observation.

        Returns:
            String representation

        Example:
            >>> repr(observation)
        """
        return f"Observation(type={self._observation_type.value}, value={self._value}, timestamp={self._timestamp})"

    def __str__(self) -> str:
        """Return string representation of the observation.

        Returns:
            String representation

        Example:
            >>> str(observation)
        """
        return f"{self._observation_type.value}: {self._value} @ {self._timestamp}"

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> obs1 == obs2
        """
        if not isinstance(other, Observation):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Return hash of the observation.

        Returns:
            Hash value

        Example:
            >>> hash(observation)
        """
        return hash(self._id)


# Export
__all__ = ["Observation"]
