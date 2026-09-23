"""
Runtime Telemetry Module

This module provides telemetry management for the Runtime package.

Purpose
-------
Provide telemetry management for the QuantsMind SDK.

Responsibilities
----------------
- Collect telemetry data
- Track telemetry points
- Support telemetry aggregation
- Handle telemetry retention

Dependencies
------------
typing (standard library)
logging (standard library)
threading (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
"""

from __future__ import annotations

import logging
import threading
from datetime import UTC, datetime

from quantsmind.runtime.constants import DEFAULT_METRICS_RETENTION
from quantsmind.runtime.types import TelemetryData, TelemetryPoint

logger = logging.getLogger(__name__)


class TelemetryCollector:
    """Concrete implementation of a telemetry collector.

    This class provides telemetry collection capabilities.

    Attributes:
        _telemetry_points: Collected telemetry points
        _retention: Retention period in seconds
        _lock: Thread lock

    Example:
        >>> collector = TelemetryCollector()
        >>> collector.record({"cpu_usage": 0.5})
    """

    def __init__(self, retention: int = DEFAULT_METRICS_RETENTION) -> None:
        """Initialize a TelemetryCollector.

        Args:
            retention: Retention period in seconds

        Example:
            >>> collector = TelemetryCollector()
        """
        self._telemetry_points: list[TelemetryPoint] = []
        self._retention = retention
        self._lock = threading.Lock()
        logger.debug("Created telemetry collector")

    @property
    def point_count(self) -> int:
        """Get the number of telemetry points.

        Returns:
            Number of points

        Example:
            >>> print(f"Point count: {collector.point_count}")
        """
        with self._lock:
            return len(self._telemetry_points)

    def record(self, data: TelemetryData) -> None:
        """Record telemetry data.

        Args:
            data: Telemetry data

        Example:
            >>> collector.record({"cpu_usage": 0.5})
        """
        with self._lock:
            point = (datetime.now(UTC).replace(tzinfo=None), data)
            self._telemetry_points.append(point)
            self._cleanup_old_points()

    def record_batch(self, data_points: list[TelemetryData]) -> None:
        """Record multiple telemetry points.

        Args:
            data_points: List of telemetry data

        Example:
            >>> collector.record_batch([{"cpu_usage": 0.5}, {"cpu_usage": 0.6}])
        """
        with self._lock:
            for data in data_points:
                point = (datetime.now(UTC).replace(tzinfo=None), data)
                self._telemetry_points.append(point)
            self._cleanup_old_points()

    def get_points(self, limit: int = 1000) -> list[TelemetryPoint]:
        """Get telemetry points.

        Args:
            limit: Maximum number of points

        Returns:
            List of telemetry points

        Example:
            >>> points = collector.get_points()
        """
        with self._lock:
            return self._telemetry_points[-limit:]

    def get_points_since(self, since: datetime) -> list[TelemetryPoint]:
        """Get telemetry points since a timestamp.

        Args:
            since: Start timestamp

        Returns:
            List of telemetry points

        Example:
            >>> points = collector.get_points_since(datetime.now(UTC).replace(tzinfo=None))
        """
        with self._lock:
            return [
                point for point in self._telemetry_points
                if point[0] >= since
            ]

    def aggregate(self, key: str, aggregation: str = "avg") -> float:
        """Aggregate telemetry data.

        Args:
            key: Data key to aggregate
            aggregation: Aggregation method (avg, min, max, sum)

        Returns:
            Aggregated value

        Example:
            >>> avg_cpu = collector.aggregate("cpu_usage", "avg")
        """
        with self._lock:
            values = [point[1].get(key, 0) for point in self._telemetry_points if key in point[1]]
            
            if not values:
                return 0.0
            
            if aggregation == "avg":
                return sum(values) / len(values)
            elif aggregation == "min":
                return min(values)
            elif aggregation == "max":
                return max(values)
            elif aggregation == "sum":
                return sum(values)
            else:
                return 0.0

    def _cleanup_old_points(self) -> None:
        """Clean up old telemetry points.

        Example:
            >>> collector._cleanup_old_points()
        """
        cutoff = datetime.now(UTC).replace(tzinfo=None).timestamp() - self._retention
        self._telemetry_points = [
            point for point in self._telemetry_points
            if point[0].timestamp() >= cutoff
        ]

    def clear(self) -> None:
        """Clear all telemetry points.

        Example:
            >>> collector.clear()
        """
        with self._lock:
            self._telemetry_points.clear()
        logger.debug("Cleared telemetry points")


# Export
__all__ = [
    "TelemetryCollector",
]
