"""Local-first instrumentation: events, metrics, and tracing.

Everything is recorded in-process. There is intentionally no transport:
no exporter, no network access, no external transmission of any kind.
Sinks are the caller's responsibility.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "TelemetryEvent",
    "Counter",
    "Gauge",
    "Span",
    "Collector",
]


@dataclass(frozen=True)
class TelemetryEvent:
    """One recorded event."""

    name: str
    timestamp: float = field(default_factory=time.time)
    attributes: dict[str, Any] = field(default_factory=dict)


class Counter:
    """Monotonically increasing in-memory counter."""

    def __init__(self, name: str) -> None:
        """Initialize at zero."""
        self._name = name
        self._value = 0
        self._lock = threading.Lock()

    @property
    def name(self) -> str:
        """Counter name."""
        return self._name

    def increment(self, amount: int = 1) -> int:
        """Add a non-negative amount; return the new value."""
        if amount < 0:
            raise ValueError(f"counter increment must be non-negative, got {amount!r}")
        with self._lock:
            self._value += amount
            return self._value

    @property
    def value(self) -> int:
        """Current value."""
        with self._lock:
            return self._value


class Gauge:
    """Settable in-memory gauge."""

    def __init__(self, name: str, initial: float = 0.0) -> None:
        """Initialize with a value."""
        self._name = name
        self._value = float(initial)
        self._lock = threading.Lock()

    @property
    def name(self) -> str:
        """Gauge name."""
        return self._name

    def set(self, value: float) -> None:
        """Set the value."""
        with self._lock:
            self._value = float(value)

    @property
    def value(self) -> float:
        """Current value."""
        with self._lock:
            return self._value


class Span:
    """A timed tracing span (context manager)."""

    def __init__(
        self, collector: Collector, name: str, attributes: dict[str, Any] | None = None
    ) -> None:
        """Bind to a collector (does not start timing yet)."""
        self._collector = collector
        self._name = name
        self._attributes = dict(attributes or {})
        self._start: float | None = None
        self.duration: float | None = None

    def __enter__(self) -> Span:
        """Start timing."""
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        """Stop timing and record a ``<name>.duration`` event."""
        assert self._start is not None
        self.duration = time.perf_counter() - self._start
        self._collector.record(f"{self._name}.duration", duration=self.duration, **self._attributes)


class Collector:
    """In-process event collector (local only, never transmits)."""

    def __init__(self) -> None:
        """Initialize empty."""
        self._events: list[TelemetryEvent] = []
        self._lock = threading.Lock()

    def record(self, name: str, **attributes: Any) -> TelemetryEvent:
        """Record an event and return it."""
        event = TelemetryEvent(name=name, attributes=dict(attributes))
        with self._lock:
            self._events.append(event)
        return event

    def events(self, name: str | None = None) -> list[TelemetryEvent]:
        """All events, optionally filtered by name."""
        with self._lock:
            if name is None:
                return list(self._events)
            return [event for event in self._events if event.name == name]

    def count(self, name: str | None = None) -> int:
        """Number of events, optionally filtered by name."""
        return len(self.events(name))

    def clear(self) -> None:
        """Drop all events."""
        with self._lock:
            self._events.clear()

    def span(self, name: str, attributes: dict[str, Any] | None = None) -> Span:
        """Create a span bound to this collector."""
        return Span(self, name, attributes)
