"""
Time Module

This module provides temporal context for entities within the QuantsMind SDK.
Time represents the ordering dimension over which state evolves (continuous, discrete, relativistic).

Purpose
-------
Provide temporal context for entities in the Foundation package.

Scientific Meaning
------------------
Time represents the ordering dimension: continuous time (classical physics),
discrete time (digital systems, quantum jumps), relativistic time (general relativity).

Responsibilities
----------------
- Manage time representations
- Support time conversions
- Enable time serialization
- Handle time intervals
- Support time queries

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
- Relativistic time dilation
- Quantum time uncertainty
- Discrete time steps
- Time series analysis
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from quantsmind.foundation.constants import DEFAULT_TIME_TYPE
from quantsmind.foundation.enums import TimeType
from quantsmind.foundation.exceptions import (
    InvalidTimeError,
    TimeConversionError,
    TimeError,
    TimeReferenceError,
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


class Time(Serializable, Validatable):
    """Concrete implementation of temporal context.

    This class provides a flexible time representation with support for
    continuous, discrete, and relativistic time models.

    Scientific Meaning
    ------------------
    In scientific computing, time represents the ordering dimension:
    continuous time (classical physics), discrete time (digital systems),
    relativistic time (general relativity).

    Attributes:
        _value: Time value (datetime for continuous, int for discrete)
        _time_type: Type of time
        _reference: Reference time (for relative time)
        _metadata: Additional metadata

    Example:
        >>> time = Time(time_type=EventType.CONTINUOUS)
        >>> print(f"Time: {time.value}")
    """

    def __init__(
        self,
        value: Optional[Any] = None,
        time_type: TimeType = TimeType.CONTINUOUS,
        reference: Optional[datetime] = None,
        metadata: Optional[MetadataDict] = None,
    ) -> None:
        """Initialize a Time.

        Args:
            value: Time value (datetime for continuous, int for discrete)
            time_type: Type of time
            reference: Optional reference time
            metadata: Optional metadata dictionary

        Raises:
            InvalidTimeError: If value is invalid

        Example:
            >>> time = Time(value=datetime.now(), time_type=TimeType.CONTINUOUS)
        """
        self._time_type: TimeType = time_type
        self._reference: Optional[datetime] = reference
        self._metadata: MetadataDict = metadata or {}

        if value is None:
            if time_type == TimeType.CONTINUOUS:
                self._value: Any = datetime.utcnow()
            else:
                self._value = 0
        else:
            self._value = value

        self._validate_value()
        logger.debug(f"Created {time_type.value} time: {self._value}")

    def _validate_value(self) -> None:
        """Validate the time value.

        Raises:
            InvalidTimeError: If value is invalid
        """
        if self._time_type == TimeType.CONTINUOUS:
            if not isinstance(self._value, datetime):
                raise InvalidTimeError(
                    f"Continuous time must be datetime, got {type(self._value)}"
                )
        elif self._time_type == TimeType.DISCRETE:
            if not isinstance(self._value, int) or self._value < 0:
                raise InvalidTimeError(
                    f"Discrete time must be non-negative integer, got {self._value}"
                )

    @property
    def value(self) -> Any:
        """Get the time value.

        Returns:
            Time value

        Example:
            >>> print(f"Time: {time.value}")
        """
        return self._value

    @property
    def time_type(self) -> TimeType:
        """Get the time type.

        Returns:
            Time type

        Example:
            >>> print(f"Type: {time.time_type}")
        """
        return self._time_type

    @property
    def reference(self) -> Optional[datetime]:
        """Get the reference time.

        Returns:
            Reference time or None

        Example:
            >>> print(f"Reference: {time.reference}")
        """
        return self._reference

    @property
    def metadata(self) -> MetadataDict:
        """Get the time metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> print(f"Metadata: {time.metadata}")
        """
        return self._metadata.copy()

    @property
    def is_continuous(self) -> bool:
        """Check if time is continuous.

        Returns:
            True if continuous, False otherwise

        Example:
            >>> if time.is_continuous:
            ...     print("Continuous time")
        """
        return self._time_type == TimeType.CONTINUOUS

    @property
    def is_discrete(self) -> bool:
        """Check if time is discrete.

        Returns:
            True if discrete, False otherwise

        Example:
            >>> if time.is_discrete:
            ...     print("Discrete time")
        """
        return self._time_type == TimeType.DISCRETE

    def set_value(self, value: Any) -> None:
        """Set the time value.

        Args:
            value: New time value

        Raises:
            InvalidTimeError: If value is invalid

        Example:
            >>> time.set_value(datetime.now())
        """
        old_value = self._value
        self._value = value
        try:
            self._validate_value()
            logger.debug(f"Updated time value: {old_value} -> {value}")
        except InvalidTimeError:
            self._value = old_value
            raise

    def set_reference(self, reference: datetime) -> None:
        """Set the reference time.

        Args:
            reference: New reference time

        Example:
            >>> time.set_reference(datetime(2024, 1, 1))
        """
        self._reference = reference
        logger.debug(f"Updated time reference: {reference}")

    # Time conversion methods
    def to_continuous(self) -> "Time":
        """Convert to continuous time.

        Returns:
            New Time instance with continuous type

        Raises:
            TimeConversionError: If conversion fails

        Example:
            >>> continuous_time = discrete_time.to_continuous()
        """
        if self._time_type == TimeType.CONTINUOUS:
            return self

        if self._reference is None:
            raise TimeReferenceError("Reference time required for conversion")

        # Convert discrete steps to datetime
        delta = timedelta(seconds=self._value)  # type: ignore
        new_value = self._reference + delta
        return Time(value=new_value, time_type=TimeType.CONTINUOUS, reference=self._reference)

    def to_discrete(self, step_size: float = 1.0) -> "Time":
        """Convert to discrete time.

        Args:
            step_size: Step size in seconds

        Returns:
            New Time instance with discrete type

        Raises:
            TimeConversionError: If conversion fails

        Example:
            >>> discrete_time = continuous_time.to_discrete(step_size=1.0)
        """
        if self._time_type == TimeType.DISCRETE:
            return self

        if self._reference is None:
            raise TimeReferenceError("Reference time required for conversion")

        # Convert datetime to discrete steps
        delta = self._value - self._reference  # type: ignore
        new_value = int(delta.total_seconds() / step_size)
        return Time(value=new_value, time_type=TimeType.DISCRETE, reference=self._reference)

    # Serializable interface implementation
    def serialize(self, format: str = "json") -> bytes:
        """Serialize the time to bytes.

        Args:
            format: Serialization format (currently only "json" supported)

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If format is not supported

        Example:
            >>> data = time.serialize(format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        value_str = self._value.isoformat() if isinstance(self._value, datetime) else str(self._value)
        reference_str = self._reference.isoformat() if self._reference else None

        data = {
            "value": value_str,
            "time_type": self._time_type.value,
            "reference": reference_str,
            "metadata": self._metadata,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes, format: str = "json") -> "Time":
        """Deserialize the time from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format (currently only "json" supported)

        Returns:
            Deserialized Time instance

        Raises:
            NotImplementedError: If format is not supported
            InvalidTimeError: If data is invalid

        Example:
            >>> time = Time.deserialize(data, format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        try:
            obj = json.loads(data.decode("utf-8"))
            time_type = TimeType(obj["time_type"])

            if time_type == TimeType.CONTINUOUS:
                value = datetime.fromisoformat(obj["value"])
            else:
                value = int(obj["value"])

            reference = datetime.fromisoformat(obj["reference"]) if obj.get("reference") else None

            return cls(
                value=value,
                time_type=time_type,
                reference=reference,
                metadata=obj.get("metadata"),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise InvalidTimeError(f"Failed to deserialize time: {e}") from e

    def is_serializable(self) -> bool:
        """Check if the time is serializable.

        Returns:
            True (times are always serializable)

        Example:
            >>> if time.is_serializable():
            ...     data = time.serialize()
        """
        return True

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = Time.get_supported_formats()
        """
        return ["json"]

    # Validatable interface implementation
    def validate(self) -> ValidationResult:
        """Validate the time.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = time.validate()
        """
        errors: list[str] = []

        try:
            self._validate_value()
        except InvalidTimeError as e:
            errors.append(str(e))

        return (len(errors) == 0, errors)

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = time.validation_errors
        """
        is_valid, errors = self.validate()
        return errors if not is_valid else []

    @property
    def validation_warnings(self) -> list[str]:
        """Get validation warnings.

        Returns:
            List of warning messages (currently empty)

        Example:
            >>> warnings = time.validation_warnings
        """
        return []

    # Object protocol methods
    def __repr__(self) -> str:
        """Return string representation of the time.

        Returns:
            String representation

        Example:
            >>> repr(time)
        """
        return f"Time(value={self._value}, type={self._time_type.value})"

    def __str__(self) -> str:
        """Return string representation of the time.

        Returns:
            String representation

        Example:
            >>> str(time)
        """
        if isinstance(self._value, datetime):
            return self._value.isoformat()
        return str(self._value)

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> time1 == time2
        """
        if not isinstance(other, Time):
            return False
        return self._value == other._value and self._time_type == other._time_type

    def __hash__(self) -> int:
        """Return hash of the time.

        Returns:
            Hash value

        Example:
            >>> hash(time)
        """
        return hash((self._value, self._time_type))


# Export
__all__ = ["Time"]
