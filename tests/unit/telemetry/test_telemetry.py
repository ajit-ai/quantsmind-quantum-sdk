"""Unit tests for quantsmind.telemetry collectors."""

from __future__ import annotations

import pytest

from quantsmind.telemetry import Collector, Counter, Gauge


class TestPrimitives:
    def test_counter(self) -> None:
        counter = Counter("hits")
        assert counter.increment() == 1
        assert counter.increment(4) == 5
        assert counter.value == 5
        with pytest.raises(ValueError):
            counter.increment(-1)

    def test_gauge(self) -> None:
        gauge = Gauge("temp", initial=20.0)
        gauge.set(21.5)
        assert gauge.value == 21.5


class TestCollector:
    def test_record_filter_count(self) -> None:
        collector = Collector()
        collector.record("a", x=1)
        collector.record("b")
        collector.record("a", x=2)
        assert collector.count() == 3
        assert collector.count("a") == 2
        assert [e.attributes["x"] for e in collector.events("a")] == [1, 2]
        collector.clear()
        assert collector.count() == 0

    def test_span_records_duration(self) -> None:
        collector = Collector()
        with collector.span("work"):
            pass
        events = collector.events("work.duration")
        assert len(events) == 1
        assert events[0].attributes["duration"] >= 0.0
