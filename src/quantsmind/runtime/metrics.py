"""
Runtime Metrics Module

This module provides metrics management for the Runtime package.

Purpose
-------
Provide metrics management for the QuantsMind SDK.

Responsibilities
----------------
- Collect metrics
- Track metric values
- Support metric aggregation
- Handle metric retention

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
from datetime import datetime

from quantsmind.runtime.constants import DEFAULT_METRICS_RETENTION
from quantsmind.runtime.types import MetricDict, MetricValue

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Concrete implementation of a metrics collector.

    This class provides metrics collection capabilities.

    Attributes:
        _metrics: Collected metrics
        _counters: Counter metrics
        _gauges: Gauge metrics
        _histograms: Histogram metrics
        _retention: Retention period in seconds
        _lock: Thread lock

    Example:
        >>> collector = MetricsCollector()
        >>> collector.increment("task_count")
        >>> collector.set_gauge("cpu_usage", 0.5)
    """

    def __init__(self, retention: int = DEFAULT_METRICS_RETENTION) -> None:
        """Initialize a MetricsCollector.

        Args:
            retention: Retention period in seconds

        Example:
            >>> collector = MetricsCollector()
        """
        self._metrics: dict[str, list[tuple]] = {}
        self._counters: dict[str, int] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}
        self._retention = retention
        self._lock = threading.Lock()
        logger.debug("Created metrics collector")

    @property
    def metric_count(self) -> int:
        """Get the number of metrics.

        Returns:
            Number of metrics

        Example:
            >>> print(f"Metric count: {collector.metric_count}")
        """
        with self._lock:
            return len(self._metrics)

    def increment(self, name: str, value: int = 1) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name
            value: Increment value

        Example:
            >>> collector.increment("task_count")
        """
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + value
            self._record_metric(name, self._counters[name])

    def decrement(self, name: str, value: int = 1) -> None:
        """Decrement a counter metric.

        Args:
            name: Metric name
            value: Decrement value

        Example:
            >>> collector.decrement("task_count")
        """
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) - value
            self._record_metric(name, self._counters[name])

    def set_gauge(self, name: str, value: float) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name
            value: Gauge value

        Example:
            >>> collector.set_gauge("cpu_usage", 0.5)
        """
        with self._lock:
            self._gauges[name] = value
            self._record_metric(name, value)

    def observe(self, name: str, value: float) -> None:
        """Observe a histogram metric.

        Args:
            name: Metric name
            value: Observed value

        Example:
            >>> collector.observe("task_duration", 1.5)
        """
        with self._lock:
            if name not in self._histograms:
                self._histograms[name] = []
            self._histograms[name].append(value)
            self._record_metric(name, value)

    def get_counter(self, name: str) -> int | None:
        """Get a counter metric.

        Args:
            name: Metric name

        Returns:
            Counter value or None

        Example:
            >>> count = collector.get_counter("task_count")
        """
        with self._lock:
            return self._counters.get(name)

    def get_gauge(self, name: str) -> float | None:
        """Get a gauge metric.

        Args:
            name: Metric name

        Returns:
            Gauge value or None

        Example:
            >>> value = collector.get_gauge("cpu_usage")
        """
        with self._lock:
            return self._gauges.get(name)

    def get_histogram(self, name: str) -> list[float] | None:
        """Get a histogram metric.

        Args:
            name: Metric name

        Returns:
            Histogram values or None

        Example:
            >>> values = collector.get_histogram("task_duration")
        """
        with self._lock:
            return self._histograms.get(name)

    def get_histogram_stats(self, name: str) -> dict[str, float]:
        """Get histogram statistics.

        Args:
            name: Metric name

        Returns:
            Histogram statistics

        Example:
            >>> stats = collector.get_histogram_stats("task_duration")
        """
        with self._lock:
            values = self._histograms.get(name, [])
            if not values:
                return {}
            
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "sum": sum(values),
            }

    def _record_metric(self, name: str, value: MetricValue) -> None:
        """Record a metric point.

        Args:
            name: Metric name
            value: Metric value
        """
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append((datetime.utcnow(), value))
        self._cleanup_old_metrics(name)

    def _cleanup_old_metrics(self, name: str) -> None:
        """Clean up old metric points.

        Args:
            name: Metric name
        """
        cutoff = datetime.utcnow().timestamp() - self._retention
        self._metrics[name] = [
            point for point in self._metrics[name]
            if point[0].timestamp() >= cutoff
        ]

    def get_all_metrics(self) -> MetricDict:
        """Get all current metrics.

        Returns:
            All metrics

        Example:
            >>> metrics = collector.get_all_metrics()
        """
        with self._lock:
            result = {}
            result.update(self._counters)
            result.update(self._gauges)
            return result

    def clear(self) -> None:
        """Clear all metrics.

        Example:
            >>> collector.clear()
        """
        with self._lock:
            self._metrics.clear()
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
        logger.debug("Cleared all metrics")


# Export
__all__ = [
    "MetricsCollector",
]
