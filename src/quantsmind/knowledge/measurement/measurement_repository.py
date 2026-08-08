"""
Measurement Repository Module

This module provides measurement repository definitions for the Knowledge package.

Purpose
-------
Provide measurement repository management for storing and retrieving measurements.

Responsibilities
----------------
- Define measurement repository structure
- Support measurement repository operations
- Support measurement repository validation
- Support measurement repository metadata

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.knowledge.enums import ProvenanceType
from quantsmind.knowledge.exceptions import MeasurementError
from quantsmind.knowledge.types import ValidationResult


class MeasurementRepository:
    """Concrete implementation of a measurement repository.

    This class provides measurement repository functionality for managing measurements.

    Attributes:
        _id: Repository ID
        _measurements: Stored measurements
        _metadata: Repository metadata

    Example:
        >>> repository = MeasurementRepository("repo_001")
        >>> repository.add_measurement(measurement)
    """

    def __init__(
        self,
        repository_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a MeasurementRepository.

        Args:
            repository_id: Repository ID
            metadata: Repository metadata

        Example:
            >>> repository = MeasurementRepository("repo_001")
        """
        if not repository_id:
            raise MeasurementError("Repository ID cannot be empty", {"repository_id": repository_id})

        self._id = repository_id
        self._measurements: Dict[str, Any] = {}
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the repository ID.

        Returns:
            Repository ID

        Example:
            >>> rid = repository.id
        """
        return self._id

    @property
    def measurements(self) -> Dict[str, Any]:
        """Get the measurements.

        Returns:
            Measurements dictionary

        Example:
            >>> measurements = repository.measurements
        """
        return self._measurements.copy()

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the repository metadata.

        Returns:
            Repository metadata

        Example:
            >>> metadata = repository.metadata
        """
        return self._metadata.copy()

    def add_measurement(self, measurement: Any) -> None:
        """Add a measurement to the repository.

        Args:
            measurement: Measurement to add

        Example:
            >>> repository.add_measurement(measurement)
        """
        meas_id = getattr(measurement, 'id', None)
        if meas_id:
            self._measurements[meas_id] = measurement

    def remove_measurement(self, measurement_id: str) -> bool:
        """Remove a measurement from the repository.

        Args:
            measurement_id: Measurement ID

        Returns:
            True if removed

        Example:
            >>> removed = repository.remove_measurement("meas_001")
        """
        if measurement_id in self._measurements:
            del self._measurements[measurement_id]
            return True
        return False

    def get_measurement(self, measurement_id: str) -> Optional[Any]:
        """Get a measurement from the repository.

        Args:
            measurement_id: Measurement ID

        Returns:
            Measurement or None

        Example:
            >>> measurement = repository.get_measurement("meas_001")
        """
        return self._measurements.get(measurement_id)

    def get_measurements_by_target(self, target: str) -> List[Any]:
        """Get measurements by target.

        Args:
            target: Target entity ID

        Returns:
            List of measurements

        Example:
            >>> measurements = repository.get_measurements_by_target("entity_001")
        """
        return [meas for meas in self._measurements.values() if getattr(meas, 'target', None) == target]

    def get_measurements_by_quantity(self, quantity: str) -> List[Any]:
        """Get measurements by quantity.

        Args:
            quantity: Measured quantity

        Returns:
            List of measurements

        Example:
            >>> measurements = repository.get_measurements_by_quantity("length")
        """
        return [meas for meas in self._measurements.values() if getattr(meas, 'quantity', None) == quantity]

    def get_measurements_by_unit(self, unit: str) -> List[Any]:
        """Get measurements by unit.

        Args:
            unit: Unit of measurement

        Returns:
            List of measurements

        Example:
            >>> measurements = repository.get_measurements_by_unit("m")
        """
        return [meas for meas in self._measurements.values() if getattr(meas, 'unit', None) == unit]

    def get_measurements_by_measurer(self, measurer: str) -> List[Any]:
        """Get measurements by measurer.

        Args:
            measurer: Measurer ID

        Returns:
            List of measurements

        Example:
            >>> measurements = repository.get_measurements_by_measurer("measurer_001")
        """
        return [meas for meas in self._measurements.values() if getattr(meas, 'measurer', None) == measurer]

    def get_measurements_by_time_range(self, start: str, end: str) -> List[Any]:
        """Get measurements within a time range.

        Args:
            start: Start timestamp
            end: End timestamp

        Returns:
            List of measurements

        Example:
            >>> measurements = repository.get_measurements_by_time_range("2024-01-01", "2024-12-31")
        """
        from datetime import datetime

        start_dt = datetime.fromisoformat(start) if isinstance(start, str) else start
        end_dt = datetime.fromisoformat(end) if isinstance(end, str) else end

        return [
            meas for meas in self._measurements.values()
            if start_dt <= getattr(meas, 'timestamp', datetime.min) <= end_dt
        ]

    def calculate_statistics(self, quantity: str) -> Dict[str, float]:
        """Calculate statistics for measurements of a quantity.

        Args:
            quantity: Measured quantity

        Returns:
            Statistics dictionary

        Example:
            >>> stats = repository.calculate_statistics("length")
        """
        quantity_measurements = self.get_measurements_by_quantity(quantity)
        values = [getattr(m, 'value', 0) for m in quantity_measurements if hasattr(m, 'value')]

        if not values:
            return {}

        return {
            "count": len(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "sum": sum(values),
        }

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the repository.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> repository.add_metadata("location", "lab")
        """
        self._metadata[key] = value

    def validate(self) -> ValidationResult:
        """Validate the repository.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = repository.validate()
        """
        errors = []

        if not self._id:
            errors.append("Repository ID cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Repository definition

        Example:
            >>> data = repository.to_dict()
        """
        return {
            "id": self._id,
            "measurement_count": len(self._measurements),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(repository)
        """
        return f"MeasurementRepository(id={self._id}, measurements={len(self._measurements)})"


# Export
__all__ = [
    "MeasurementRepository",
]
