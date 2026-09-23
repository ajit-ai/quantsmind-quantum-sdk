"""
Galactic Coordinate Module

This module provides galactic coordinate definitions for the Scientific package.

Purpose
-------
Provide galactic coordinate system implementation.

Responsibilities
----------------
- Define galactic coordinates
- Support coordinate transformations
- Support coordinate operations
- Support coordinate validation

Dependencies
------------
typing (standard library)
math (standard library)
quantsmind.scientific.interfaces (scientific interfaces)
quantsmind.scientific.exceptions (scientific exceptions)
quantsmind.scientific.types (scientific types)
"""

from __future__ import annotations

import math
from typing import Any

from quantsmind.scientific.exceptions import CoordinateError
from quantsmind.scientific.interfaces import ICoordinate
from quantsmind.scientific.types import CoordinateTriple, CoordinateValue


class GalacticCoordinate(ICoordinate):
    """Concrete implementation of galactic coordinates.

    This class provides galactic coordinate functionality.

    Attributes:
        _lon: Galactic longitude (degrees)
        _b: Galactic latitude (degrees)
        _distance: Distance from galactic center
        _metadata: Coordinate metadata

    Example:
        >>> coord = GalacticCoordinate(45.0, 30.0, 8.5)
        >>> coord.coordinates()
    """

    def __init__(
        self,
        lon: CoordinateValue,
        b: CoordinateValue,
        distance: CoordinateValue = 8.5,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a GalacticCoordinate.

        Args:
            lon: Galactic longitude (degrees)
            b: Galactic latitude (degrees)
            distance: Distance from galactic center (kpc)
            metadata: Coordinate metadata

        Example:
            >>> coord = GalacticCoordinate(45.0, 30.0, 8.5)
        """
        self._lon = lon
        self._b = b
        self._distance = distance
        self._metadata = metadata or {}

    @property
    def lon(self) -> CoordinateValue:
        """Get the galactic longitude.

        Returns:
            Galactic longitude (degrees)

        Example:
            >>> print(f"Lon: {coord.lon}")
        """
        return self._lon

    @property
    def b(self) -> CoordinateValue:
        """Get the galactic latitude.

        Returns:
            Galactic latitude (degrees)

        Example:
            >>> print(f"B: {coord.b}")
        """
        return self._b

    @property
    def distance(self) -> CoordinateValue:
        """Get the distance from galactic center.

        Returns:
            Distance (kpc)

        Example:
            >>> print(f"Distance: {coord.distance}")
        """
        return self._distance

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the coordinate metadata.

        Returns:
            Coordinate metadata

        Example:
            >>> print(f"Metadata: {coord.metadata}")
        """
        return self._metadata.copy()

    def coordinates(self) -> CoordinateTriple:
        """Get the coordinate values.

        Returns:
            Coordinate values (lon, b, distance)

        Example:
            >>> coords = coord.coordinates()
        """
        return (self._lon, self._b, self._distance)

    def system(self) -> str:
        """Get the coordinate system.

        Returns:
            Coordinate system name

        Example:
            >>> print(f"System: {coord.system()}")
        """
        return "galactic"

    def magnitude(self) -> float:
        """Calculate the magnitude.

        Returns:
            Magnitude (distance)

        Example:
            >>> mag = coord.magnitude()
        """
        return self._distance

    def to_equatorial(self) -> tuple[float, float]:
        """Convert to equatorial coordinates (RA, Dec).

        Returns:
            Equatorial coordinates (ra, dec) in degrees

        Note:
            This is a simplified transformation. Real astronomical transformations
            require more complex calculations.

        Example:
            >>> ra, dec = coord.to_equatorial()
        """
        # Simplified transformation (real implementation would use proper astronomical formulas)
        lon_rad = math.radians(self._lon)
        b_rad = math.radians(self._b)
        
        # Approximate transformation
        ra = (lon_rad + math.pi) * 180 / math.pi
        dec = b_rad * 180 / math.pi
        
        return (ra % 360, dec)

    def transform_to(self, target_system: str) -> ICoordinate:
        """Transform to a different coordinate system.

        Args:
            target_system: Target coordinate system

        Returns:
            Transformed coordinate

        Raises:
            CoordinateError: If transformation not supported

        Example:
            >>> transformed = coord.transform_to("equatorial")
        """
        if target_system == "galactic":
            return self
        elif target_system == "equatorial":
            from quantsmind.scientific.coordinates.equatorial import EquatorialCoordinate
            ra, dec = self.to_equatorial()
            return EquatorialCoordinate(ra, dec, self._distance)
        else:
            raise CoordinateError(f"Transformation to {target_system} not supported")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Coordinate definition

        Example:
            >>> data = coord.to_dict()
        """
        return {
            "system": self.system(),
            "lon": self._lon,
            "b": self._b,
            "distance": self._distance,
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(coord)
        """
        return f"GalacticCoordinate(lon={self._lon}, b={self._b}, distance={self._distance})"


# Export
__all__ = [
    "GalacticCoordinate",
]
