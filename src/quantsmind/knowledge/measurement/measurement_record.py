"""
Measurement Record Module

This module provides measurement record definitions for the Knowledge package.

Purpose
-------
Provide measurement record management for tracking measurements.

Responsibilities
----------------
- Define measurement record structure
- Support measurement record operations
- Support measurement record validation
- Support measurement record metadata

Dependencies
------------
typing (standard library)
datetime (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from quantsmind.knowledge.exceptions import MeasurementError
from quantsmind.knowledge.types import ValidationResult


class MeasurementRecord:
    """Concrete implementation of a measurement record.

    This class provides measurement record functionality.

    Attributes:
        _id: Record ID
        _timestamp: Measurement timestamp
        _measurer: Measurer ID
        _target: Target entity ID
        _quantity: Measured quantity
        _unit: Unit of measurement
        _value: Measured value
        _uncertainty: Measurement uncertainty
        _metadata: Record metadata

    Example:
        >>> record = MeasurementRecord("meas_001", "measurer_001", "entity_001", "length", "m", 42.0)
        >>> record.value
    """

    def __init__(
        self,
        record_id: str,
        measurer: str,
        target: str,
        quantity: str,
        unit: str,
        value: float,
        uncertainty: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a MeasurementRecord.

        Args:
            record_id: Record ID
            measurer: Measurer ID
            target: Target entity ID
            quantity: Measured quantity
            unit: Unit of measurement
            value: Measured value
            uncertainty: Measurement uncertainty
            metadata: Record metadata

        Example:
            >>> record = MeasurementRecord("meas_001", "measurer_001", "entity_001", "length", "m", 42.0)
        """
        if not record_id:
            raise MeasurementError("Record ID cannot be empty", {"record_id": record_id})

        if not measurer:
            raise MeasurementError("Measurer cannot be empty", {"measurer": measurer})

        if not target:
            raise MeasurementError("Target cannot be empty", {"target": target})

        if not quantity:
            raise MeasurementError("Quantity cannot be empty", {"quantity": quantity})

        if not unit:
            raise MeasurementError("Unit cannot be empty", {"unit": unit})

        self._id = record_id
        self._timestamp = datetime.utcnow()
        self._measurer = measurer
        self._target = target
        self._quantity = quantity
        self._unit = unit
        self._value = value
        self._uncertainty = uncertainty
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the record ID.

        Returns:
            Record ID

        Example:
            >>> rid = record.id
        """
        return self._id

    @property
    def timestamp(self) -> datetime:
        """Get the measurement timestamp.

        Returns:
            Timestamp

        Example:
            >>> timestamp = record.timestamp
        """
        return self._timestamp

    @property
    def measurer(self) -> str:
        """Get the measurer ID.

        Returns:
            Measurer ID

        Example:
            >>> measurer = record.measurer
        """
        return self._measurer

    @property
    def target(self) -> str:
        """Get the target entity ID.

        Returns:
            Target entity ID

        Example:
            >>> target = record.target
        """
        return self._target

    @property
    def quantity(self) -> str:
        """Get the measured quantity.

        Returns:
            Measured quantity

        Example:
            >>> quantity = record.quantity
        """
        return self._quantity

    @property
    def unit(self) -> str:
        """Get the unit of measurement.

        Returns:
            Unit of measurement

        Example:
            >>> unit = record.unit
        """
        return self._unit

    @property
    def value(self) -> float:
        """Get the measured value.

        Returns:
            Measured value

        Example:
            >>> value = record.value
        """
        return self._value

    @property
    def uncertainty(self) -> float | None:
        """Get the measurement uncertainty.

        Returns:
            Measurement uncertainty

        Example:
            >>> uncertainty = record.uncertainty
        """
        return self._uncertainty

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the record metadata.

        Returns:
            Record metadata

        Example:
            >>> metadata = record.metadata
        """
        return self._metadata.copy()

    def set_value(self, value: float) -> None:
        """Set the measured value.

        Args:
            value: Measured value

        Example:
            >>> record.set_value(43.0)
        """
        self._value = value

    def set_uncertainty(self, uncertainty: float) -> None:
        """Set the measurement uncertainty.

        Args:
            uncertainty: Measurement uncertainty

        Example:
            >>> record.set_uncertainty(0.1)
        """
        self._uncertainty = uncertainty

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the record.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> record.add_metadata("location", "lab")
        """
        self._metadata[key] = value

    def validate(self) -> ValidationResult:
        """Validate the record.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = record.validate()
        """
        errors = []

        if not self._id:
            errors.append("Record ID cannot be empty")

        if not self._measurer:
            errors.append("Measurer cannot be empty")

        if not self._target:
            errors.append("Target cannot be empty")

        if not self._quantity:
            errors.append("Quantity cannot be empty")

        if not self._unit:
            errors.append("Unit cannot be empty")

        if self._uncertainty is not None and self._uncertainty < 0:
            errors.append("Uncertainty cannot be negative")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Record definition

        Example:
            >>> data = record.to_dict()
        """
        return {
            "id": self._id,
            "timestamp": self._timestamp.isoformat(),
            "measurer": self._measurer,
            "target": self._target,
            "quantity": self._quantity,
            "unit": self._unit,
            "value": self._value,
            "uncertainty": self._uncertainty,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(record)
        """
        return f"MeasurementRecord(id={self._id}, quantity={self._quantity}, value={self._value} {self._unit})"


# Export
__all__ = [
    "MeasurementRecord",
]
