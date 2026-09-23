"""
Observation Module

This module provides observation definitions for the Scientific package.

Purpose
-------
Provide observation record and management.

Responsibilities
----------------
- Define observation structure
- Support observation metadata
- Support observation validation
- Support observation history

Dependencies
------------
typing (standard library)
datetime (standard library)
quantsmind.scientific.interfaces (scientific interfaces)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from quantsmind.scientific.interfaces import IMeasurement
from quantsmind.scientific.types import ObservableID, ObservationID, ObserverID


class Observation:
    """Concrete implementation of an observation record.

    This class provides observation record functionality.

    Attributes:
        _observation_id: Observation identifier
        _observable_id: Observable identifier
        _observer_id: Observer identifier
        _measurement: Measurement result
        _timestamp: Observation timestamp
        _metadata: Observation metadata

    Example:
        >>> observation = Observation("obs_001", "temp_001", "sensor_001", measurement)
        >>> observation.measurement()
    """

    def __init__(
        self,
        observation_id: ObservationID,
        observable_id: ObservableID,
        observer_id: ObserverID,
        measurement: IMeasurement,
        timestamp: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an Observation.

        Args:
            observation_id: Observation identifier
            observable_id: Observable identifier
            observer_id: Observer identifier
            measurement: Measurement result
            timestamp: Observation timestamp
            metadata: Observation metadata

        Example:
            >>> observation = Observation("obs_001", "temp_001", "sensor_001", measurement)
        """
        self._observation_id = observation_id
        self._observable_id = observable_id
        self._observer_id = observer_id
        self._measurement = measurement
        self._timestamp = timestamp or datetime.now(UTC).replace(tzinfo=None)
        self._metadata = metadata or {}

    @property
    def observation_id(self) -> ObservationID:
        """Get the observation identifier.

        Returns:
            Observation identifier

        Example:
            >>> print(f"ID: {observation.observation_id}")
        """
        return self._observation_id

    @property
    def observable_id(self) -> ObservableID:
        """Get the observable identifier.

        Returns:
            Observable identifier

        Example:
            >>> print(f"Observable ID: {observation.observable_id}")
        """
        return self._observable_id

    @property
    def observer_id(self) -> ObserverID:
        """Get the observer identifier.

        Returns:
            Observer identifier

        Example:
            >>> print(f"Observer ID: {observation.observer_id}")
        """
        return self._observer_id

    @property
    def measurement(self) -> IMeasurement:
        """Get the measurement result.

        Returns:
            Measurement result

        Example:
            >>> print(f"Measurement: {observation.measurement}")
        """
        return self._measurement

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
    def metadata(self) -> dict[str, Any]:
        """Get the observation metadata.

        Returns:
            Observation metadata

        Example:
            >>> print(f"Metadata: {observation.metadata}")
        """
        return self._metadata.copy()

    def is_valid(self) -> bool:
        """Check if the observation is valid.

        Returns:
            True if valid, False otherwise

        Example:
            >>> if observation.is_valid():
            ...     print("Valid observation")
        """
        # Check if measurement is within reasonable bounds
        try:
            value = self._measurement.value
            uncertainty = self._measurement.uncertainty
            
            # Basic validation: uncertainty should be positive
            if uncertainty < 0:
                return False
            
            # Value should be finite
            return isinstance(value, (int, float))
        except Exception:
            return False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Observation record

        Example:
            >>> data = observation.to_dict()
        """
        return {
            "observation_id": self._observation_id,
            "observable_id": self._observable_id,
            "observer_id": self._observer_id,
            "measurement": self._measurement.to_dict(),
            "timestamp": self._timestamp.isoformat(),
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(observation)
        """
        return f"Observation(id={self._observation_id}, observable={self._observable_id}, observer={self._observer_id})"


class ObservationRecord:
    """Concrete implementation of an observation record collection.

    This class provides observation record collection functionality.

    Attributes:
        _observations: List of observations
        _metadata: Record metadata

    Example:
        >>> record = ObservationRecord()
        >>> record.add_observation(observation)
    """

    def __init__(self, metadata: dict[str, Any] | None = None) -> None:
        """Initialize an ObservationRecord.

        Args:
            metadata: Record metadata

        Example:
            >>> record = ObservationRecord()
        """
        self._observations: List[Observation] = []
        self._metadata = metadata or {}

    @property
    def observation_count(self) -> int:
        """Get the number of observations.

        Returns:
            Number of observations

        Example:
            >>> print(f"Count: {record.observation_count}")
        """
        return len(self._observations)

    def add_observation(self, observation: Observation) -> None:
        """Add an observation to the record.

        Args:
            observation: Observation to add

        Example:
            >>> record.add_observation(observation)
        """
        self._observations.append(observation)

    def get_observations(self, observable_id: ObservableID | None = None) -> List[Observation]:
        """Get observations, optionally filtered by observable.

        Args:
            observable_id: Optional observable identifier filter

        Returns:
            List of observations

        Example:
            >>> observations = record.get_observations("temp_001")
        """
        if observable_id is None:
            return self._observations.copy()
        
        return [obs for obs in self._observations if obs.observable_id == observable_id]

    def get_latest_observation(self, observable_id: ObservableID) -> Observation | None:
        """Get the latest observation for an observable.

        Args:
            observable_id: Observable identifier

        Returns:
            Latest observation or None

        Example:
            >>> latest = record.get_latest_observation("temp_001")
        """
        observations = self.get_observations(observable_id)
        if not observations:
            return None
        
        return max(observations, key=lambda obs: obs.timestamp)

    def clear(self) -> None:
        """Clear all observations.

        Example:
            >>> record.clear()
        """
        self._observations.clear()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Record data

        Example:
            >>> data = record.to_dict()
        """
        return {
            "observation_count": self.observation_count,
            "observations": [obs.to_dict() for obs in self._observations],
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(record)
        """
        return f"ObservationRecord(count={self.observation_count})"


# Export
__all__ = [
    "Observation",
    "ObservationRecord",
]
