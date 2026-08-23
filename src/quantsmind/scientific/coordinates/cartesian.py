"""
Cartesian Coordinate Module

This module provides Cartesian coordinate definitions for the Scientific package.

Purpose
-------
Provide Cartesian coordinate system implementation.

Responsibilities
----------------
- Define Cartesian coordinates
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


class CartesianCoordinate(ICoordinate):
    """Concrete implementation of Cartesian coordinates.

    This class provides Cartesian coordinate functionality.

    Attributes:
        _x: X coordinate
        _y: Y coordinate
        _z: Z coordinate
        _metadata: Coordinate metadata

    Example:
        >>> coord = CartesianCoordinate(1.0, 2.0, 3.0)
        >>> coord.coordinates()
    """

    def __init__(
        self,
        x: CoordinateValue,
        y: CoordinateValue,
        z: CoordinateValue = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a CartesianCoordinate.

        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate (default 0.0 for 2D)
            metadata: Coordinate metadata

        Example:
            >>> coord = CartesianCoordinate(1.0, 2.0, 3.0)
        """
        self._x = x
        self._y = y
        self._z = z
        self._metadata = metadata or {}

    @property
    def x(self) -> CoordinateValue:
        """Get the X coordinate.

        Returns:
            X coordinate

        Example:
            >>> print(f"X: {coord.x}")
        """
        return self._x

    @property
    def y(self) -> CoordinateValue:
        """Get the Y coordinate.

        Returns:
            Y coordinate

        Example:
            >>> print(f"Y: {coord.y}")
        """
        return self._y

    @property
    def z(self) -> CoordinateValue:
        """Get the Z coordinate.

        Returns:
            Z coordinate

        Example:
            >>> print(f"Z: {coord.z}")
        """
        return self._z

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
            Coordinate values (x, y, z)

        Example:
            >>> coords = coord.coordinates()
        """
        return (self._x, self._y, self._z)

    def system(self) -> str:
        """Get the coordinate system.

        Returns:
            Coordinate system name

        Example:
            >>> print(f"System: {coord.system()}")
        """
        return "cartesian"

    def magnitude(self) -> float:
        """Calculate the magnitude (distance from origin).

        Returns:
            Magnitude

        Example:
            >>> mag = coord.magnitude()
        """
        return math.sqrt(self._x ** 2 + self._y ** 2 + self._z ** 2)

    def distance_to(self, other: ICoordinate) -> float:
        """Calculate distance to another coordinate.

        Args:
            other: Other coordinate

        Returns:
            Distance

        Raises:
            CoordinateError: If coordinate systems don't match

        Example:
            >>> dist = coord.distance_to(other_coord)
        """
        if other.system() != "cartesian":
            raise CoordinateError("Cannot calculate distance between different coordinate systems")
        
        ox, oy, oz = other.coordinates()
        return math.sqrt((self._x - ox) ** 2 + (self._y - oy) ** 2 + (self._z - oz) ** 2)

    def to_polar(self) -> tuple[float, float]:
        """Convert to polar coordinates (2D).

        Returns:
            Polar coordinates (r, theta)

        Example:
            >>> r, theta = coord.to_polar()
        """
        r = math.sqrt(self._x ** 2 + self._y ** 2)
        theta = math.atan2(self._y, self._x)
        return (r, theta)

    def to_spherical(self) -> tuple[float, float, float]:
        """Convert to spherical coordinates.

        Returns:
            Spherical coordinates (r, theta, phi)

        Example:
            >>> r, theta, phi = coord.to_spherical()
        """
        r = self.magnitude()
        theta = math.atan2(self._y, self._x)
        phi = math.atan2(math.sqrt(self._x ** 2 + self._y ** 2), self._z)
        return (r, theta, phi)

    def transform_to(self, target_system: str) -> ICoordinate:
        """Transform to a different coordinate system.

        Args:
            target_system: Target coordinate system

        Returns:
            Transformed coordinate

        Raises:
            CoordinateError: If transformation not supported

        Example:
            >>> transformed = coord.transform_to("spherical")
        """
        if target_system == "cartesian":
            return self
        elif target_system == "polar":
            from quantsmind.scientific.coordinates.polar import PolarCoordinate
            r, theta = self.to_polar()
            return PolarCoordinate(r, theta)
        elif target_system == "spherical":
            from quantsmind.scientific.coordinates.spherical import SphericalCoordinate
            r, theta, phi = self.to_spherical()
            return SphericalCoordinate(r, theta, phi)
        elif target_system == "cylindrical":
            from quantsmind.scientific.coordinates.cylindrical import CylindricalCoordinate
            r, theta = self.to_polar()
            return CylindricalCoordinate(r, theta, self._z)
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
            "x": self._x,
            "y": self._y,
            "z": self._z,
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(coord)
        """
        return f"CartesianCoordinate(x={self._x}, y={self._y}, z={self._z})"


# Export
__all__ = [
    "CartesianCoordinate",
]
