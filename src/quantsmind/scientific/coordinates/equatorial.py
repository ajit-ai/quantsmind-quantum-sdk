"""
Equatorial Coordinate Module

This module provides equatorial coordinate definitions for the Scientific package.

Purpose
-------
Provide equatorial coordinate system implementation.

Responsibilities
----------------
- Define equatorial coordinates
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


class EquatorialCoordinate(ICoordinate):
    """Concrete implementation of equatorial coordinates.

    This class provides equatorial coordinate functionality.

    Attributes:
        _ra: Right ascension (degrees)
        _dec: Declination (degrees)
        _distance: Distance from observer
        _metadata: Coordinate metadata

    Example:
        >>> coord = EquatorialCoordinate(45.0, 30.0, 100.0)
        >>> coord.coordinates()
    """

    def __init__(
        self,
        ra: CoordinateValue,
        dec: CoordinateValue,
        distance: CoordinateValue = 100.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an EquatorialCoordinate.

        Args:
            ra: Right ascension (degrees)
            dec: Declination (degrees)
            distance: Distance from observer (arbitrary units)
            metadata: Coordinate metadata

        Example:
            >>> coord = EquatorialCoordinate(45.0, 30.0, 100.0)
        """
        self._ra = ra
        self._dec = dec
        self._distance = distance
        self._metadata = metadata or {}

    @property
    def ra(self) -> CoordinateValue:
        """Get the right ascension.

        Returns:
            Right ascension (degrees)

        Example:
            >>> print(f"RA: {coord.ra}")
        """
        return self._ra

    @property
    def dec(self) -> CoordinateValue:
        """Get the declination.

        Returns:
            Declination (degrees)

        Example:
            >>> print(f"Dec: {coord.dec}")
        """
        return self._dec

    @property
    def distance(self) -> CoordinateValue:
        """Get the distance from observer.

        Returns:
            Distance (arbitrary units)

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
            Coordinate values (ra, dec, distance)

        Example:
            >>> coords = coord.coordinates()
        """
        return (self._ra, self._dec, self._distance)

    def system(self) -> str:
        """Get the coordinate system.

        Returns:
            Coordinate system name

        Example:
            >>> print(f"System: {coord.system()}")
        """
        return "equatorial"

    def magnitude(self) -> float:
        """Calculate the magnitude.

        Returns:
            Magnitude (distance)

        Example:
            >>> mag = coord.magnitude()
        """
        return self._distance

    def to_galactic(self) -> tuple[float, float]:
        """Convert to galactic coordinates (l, b).

        Returns:
            Galactic coordinates (l, b) in degrees

        Note:
            This is a simplified transformation. Real astronomical transformations
            require more complex calculations.

        Example:
            >>> l, b = coord.to_galactic()
        """
        # Simplified transformation (real implementation would use proper astronomical formulas)
        ra_rad = math.radians(self._ra)
        dec_rad = math.radians(self._dec)
        
        # Approximate transformation
        lon = (ra_rad - math.pi) * 180 / math.pi
        b = dec_rad * 180 / math.pi
        
        return (l % 360, b)

    def to_cartesian(self) -> tuple[float, float, float]:
        """Convert to Cartesian coordinates.

        Returns:
            Cartesian coordinates (x, y, z)

        Example:
            >>> x, y, z = coord.to_cartesian()
        """
        ra_rad = math.radians(self._ra)
        dec_rad = math.radians(self._dec)
        
        x = self._distance * math.cos(dec_rad) * math.cos(ra_rad)
        y = self._distance * math.cos(dec_rad) * math.sin(ra_rad)
        z = self._distance * math.sin(dec_rad)
        
        return (x, y, z)

    def transform_to(self, target_system: str) -> ICoordinate:
        """Transform to a different coordinate system.

        Args:
            target_system: Target coordinate system

        Returns:
            Transformed coordinate

        Raises:
            CoordinateError: If transformation not supported

        Example:
            >>> transformed = coord.transform_to("galactic")
        """
        if target_system == "equatorial":
            return self
        elif target_system == "galactic":
            from quantsmind.scientific.coordinates.galactic import GalacticCoordinate
            lon, b = self.to_galactic()
            return GalacticCoordinate(l, b, self._distance)
        elif target_system == "cartesian":
            from quantsmind.scientific.coordinates.cartesian import CartesianCoordinate
            x, y, z = self.to_cartesian()
            return CartesianCoordinate(x, y, z)
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
            "ra": self._ra,
            "dec": self._dec,
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
        return f"EquatorialCoordinate(ra={self._ra}, dec={self._dec}, distance={self._distance})"


# Export
__all__ = [
    "EquatorialCoordinate",
]
