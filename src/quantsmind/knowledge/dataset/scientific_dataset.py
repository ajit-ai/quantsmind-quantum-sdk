"""
Scientific Dataset Module

This module provides scientific dataset definitions for the Knowledge package.

Purpose
-------
Provide scientific dataset management with measurement and observation support.

Responsibilities
----------------
- Define scientific dataset structure
- Support measurement data
- Support observation data
- Support scientific metadata
- Support scientific validation

Dependencies
------------
typing (standard library)
quantsmind.knowledge.dataset.dataset (dataset)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.knowledge.dataset.dataset import Dataset
from quantsmind.knowledge.enums import DatasetType
from quantsmind.knowledge.exceptions import DatasetError
from quantsmind.knowledge.types import (
    DatasetData,
    DatasetSchema,
    MeasurementData,
    ObservationData,
    ValidationResult,
)


class ScientificDataset(Dataset):
    """Concrete implementation of a scientific dataset.

    This class provides scientific dataset functionality with measurement and observation support.

    Attributes:
        _measurements: Measurement records
        _observations: Observation records
        _units: Scientific units
        _uncertainties: Measurement uncertainties

    Example:
        >>> dataset = ScientificDataset("experiment_data")
        >>> dataset.add_measurement({"value": 42.0, "unit": "m", "uncertainty": 0.1})
    """

    def __init__(
        self,
        name: str,
        schema: DatasetSchema | None = None,
        data: DatasetData | None = None,
        metadata: dict[str, Any] | None = None,
        units: dict[str, str] | None = None,
    ) -> None:
        """Initialize a ScientificDataset.

        Args:
            name: Dataset name
            schema: Dataset schema
            data: Dataset data
            metadata: Dataset metadata
            units: Scientific units mapping

        Example:
            >>> dataset = ScientificDataset("experiment_data")
        """
        super().__init__(
            name=name,
            dataset_type=DatasetType.SCIENTIFIC,
            schema=schema,
            data=data,
            metadata=metadata,
        )
        self._measurements: list[MeasurementData] = []
        self._observations: list[ObservationData] = []
        self._units = units or {}
        self._uncertainties: dict[str, float] = {}

    @property
    def measurements(self) -> list[MeasurementData]:
        """Get the measurements.

        Returns:
            Measurement records

        Example:
            >>> measurements = dataset.measurements
        """
        return self._measurements.copy()

    @property
    def observations(self) -> list[ObservationData]:
        """Get the observations.

        Returns:
            Observation records

        Example:
            >>> observations = dataset.observations
        """
        return self._observations.copy()

    @property
    def units(self) -> dict[str, str]:
        """Get the units.

        Returns:
            Units mapping

        Example:
            >>> units = dataset.units
        """
        return self._units.copy()

    @property
    def uncertainties(self) -> dict[str, float]:
        """Get the uncertainties.

        Returns:
            Uncertainties mapping

        Example:
            >>> uncertainties = dataset.uncertainties
        """
        return self._uncertainties.copy()

    def add_measurement(self, measurement: MeasurementData) -> None:
        """Add a measurement to the dataset.

        Args:
            measurement: Measurement data

        Raises:
            DatasetError: If measurement is invalid

        Example:
            >>> dataset.add_measurement({"value": 42.0, "unit": "m", "uncertainty": 0.1})
        """
        if not isinstance(measurement, dict):
            raise DatasetError("Measurement must be a dictionary", {"measurement": measurement})

        if "value" not in measurement:
            raise DatasetError("Measurement must have a value", {"measurement": measurement})

        self._measurements.append(measurement)
        self._updated_at = self._updated_at

    def add_measurements(self, measurements: list[MeasurementData]) -> None:
        """Add multiple measurements to the dataset.

        Args:
            measurements: Measurement data list

        Example:
            >>> dataset.add_measurements([{"value": 42.0}, {"value": 43.0}])
        """
        for measurement in measurements:
            self.add_measurement(measurement)

    def add_observation(self, observation: ObservationData) -> None:
        """Add an observation to the dataset.

        Args:
            observation: Observation data

        Raises:
            DatasetError: If observation is invalid

        Example:
            >>> from datetime import datetime
            >>> dataset.add_observation({"timestamp": datetime.utcnow(), "data": {"value": 42}})
        """
        if not isinstance(observation, dict):
            raise DatasetError("Observation must be a dictionary", {"observation": observation})

        self._observations.append(observation)
        self._updated_at = self._updated_at

    def add_observations(self, observations: list[ObservationData]) -> None:
        """Add multiple observations to the dataset.

        Args:
            observations: Observation data list

        Example:
            >>> dataset.add_observations([{"data": {"value": 42}}, {"data": {"value": 43}}])
        """
        for observation in observations:
            self.add_observation(observation)

    def set_unit(self, field: str, unit: str) -> None:
        """Set unit for a field.

        Args:
            field: Field name
            unit: Unit

        Example:
            >>> dataset.set_unit("length", "m")
        """
        self._units[field] = unit

    def set_uncertainty(self, field: str, uncertainty: float) -> None:
        """Set uncertainty for a field.

        Args:
            field: Field name
            uncertainty: Uncertainty value

        Example:
            >>> dataset.set_uncertainty("length", 0.1)
        """
        self._uncertainties[field] = uncertainty

    def get_measurements_by_field(self, field: str) -> list[MeasurementData]:
        """Get measurements for a specific field.

        Args:
            field: Field name

        Returns:
            Measurement records

        Example:
            >>> measurements = dataset.get_measurements_by_field("length")
        """
        return [m for m in self._measurements if field in m]

    def get_observations_by_time_range(self, start: str, end: str) -> list[ObservationData]:
        """Get observations within a time range.

        Args:
            start: Start timestamp
            end: End timestamp

        Returns:
            Observation records

        Example:
            >>> observations = dataset.get_observations_by_time_range("2024-01-01", "2024-12-31")
        """
        return [
            obs
            for obs in self._observations
            if start <= obs.get("timestamp", "") <= end
        ]

    def calculate_statistics(self, field: str) -> dict[str, float]:
        """Calculate statistics for a field.

        Args:
            field: Field name

        Returns:
            Statistics dictionary

        Example:
            >>> stats = dataset.calculate_statistics("value")
        """
        values = [m.get("value", 0) for m in self._measurements if field in m]

        if not values:
            return {}

        return {
            "count": len(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }

    def validate(self) -> ValidationResult:
        """Validate the scientific dataset.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = dataset.validate()
        """
        errors = []

        # Validate base dataset
        base_valid, base_errors = super().validate()
        errors.extend(base_errors)

        # Validate measurements
        for i, measurement in enumerate(self._measurements):
            if "value" not in measurement:
                errors.append(f"Measurement {i} missing value")

        # Validate units
        for field, unit in self._units.items():
            if not isinstance(unit, str):
                errors.append(f"Unit for field {field} must be a string")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dataset definition

        Example:
            >>> data = dataset.to_dict()
        """
        data = super().to_dict()
        data.update({
            "measurements_count": len(self._measurements),
            "observations_count": len(self._observations),
            "units": self._units,
            "uncertainties": self._uncertainties,
        })
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(dataset)
        """
        return f"ScientificDataset(id={self._id}, name={self._name}, measurements={len(self._measurements)}, observations={len(self._observations)})"


# Export
__all__ = [
    "ScientificDataset",
]
