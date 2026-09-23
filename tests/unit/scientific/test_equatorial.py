"""Unit tests for the equatorial coordinate conversions."""

from __future__ import annotations

from quantsmind.scientific.coordinates.equatorial import EquatorialCoordinate


class TestEquatorialConversions:
    """Galactic conversion must use the computed longitude (regression: NameError)."""

    def test_to_galactic_returns_pair(self) -> None:
        coord = EquatorialCoordinate(180.0, 45.0, 10.0)
        lon, b = coord.to_galactic()
        assert lon == 0.0
        assert b == 45.0

    def test_transform_to_galactic(self) -> None:
        coord = EquatorialCoordinate(180.0, 45.0, 10.0)
        transformed = coord.transform_to("galactic")
        assert type(transformed).__name__ == "GalacticCoordinate"
