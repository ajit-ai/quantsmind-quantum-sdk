"""Unit tests for math geometry and topology value objects."""

from __future__ import annotations

from quantsmind.math.geometry import Point
from quantsmind.math.topology import TopologicalSpace


class TestPoint:
    def test_coordinates_and_dimension(self) -> None:
        point = Point([1.0, 2.0, 3.0])
        assert point.coordinates == [1.0, 2.0, 3.0]
        assert point.dimension == 3


class TestTopologicalSpace:
    def test_open_set_membership(self) -> None:
        space = TopologicalSpace({1, 2})
        space.add_open_set({1})
        assert space.is_open({1}) is True
        assert space.is_open({2}) is False
        assert space.elements == {1, 2}
