"""
Cylindrical Coordinate Module

This module provides cylindrical coordinate definitions for the Scientific package.

Purpose
-------
Provide cylindrical coordinate system implementation.

Responsibilities
----------------
- Define cylindrical coordinates
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


class CylindricalCoordinate(ICoordinate):
    """Concrete implementation of cylindrical coordinates.

    This class provides cylindrical coordinate functionality.

    Attributes:
        _r: Radial distance
        _theta: Angular coordinate (radians)
        _z: Height coordinate
        _metadata: Coordinate metadata

    Example:
        >>> coord = CylindricalCoordinate(1.0, math.pi/4, 2.0)
        >>> coord.coordinates()
    """

    def __init__(
        self,
        r: CoordinateValue,
        theta: CoordinateValue,
        z: CoordinateValue,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a CylindricalCoordinate.

        Args:
            r: Radial distance
            theta: Angular coordinate (radians)
            z: Height coordinate
            metadata: Coordinate metadata

        Example:
            >>> coord = CylindricalCoordinate(1.0, math.pi/4, 2.0)
        """
        if r < 0:
            raise CoordinateError("Radial distance cannot be negative", coordinate="r")

        self._r = r
        self._theta = theta
        self._z = z
        self._metadata = metadata or {}

    @property
    def r(self) -> CoordinateValue:
        """Get the radial distance.

        Returns:
            Radial distance

        Example:
            >>> print(f"R: {coord.r}")
        """
        return self._r

    @property
    def theta(self) -> CoordinateValue:
        """Get the angular coordinate.

        Returns:
            Angular coordinate (radians)

        Example:
            >>> print(f"Theta: {coord.theta}")
        """
        return self._theta

    @property
    def z(self) -> CoordinateValue:
        """Get the height coordinate.

        Returns:
            Height coordinate

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
            Coordinate values (r, theta, z)

        Example:
            >>> coords = coord.coordinates()
        """
        return (self._r, self._theta, self._z)

    def system(self) -> str:
        """Get the coordinate system.

        Returns:
            Coordinate system name

        Example:
            >>> print(f"System: {coord.system()}")
        """
        return "cylindrical"

    def magnitude(self) -> float:
        """Calculate the magnitude.

        Returns:
            Magnitude

        Example:
            >>> mag = coord.magnitude()
        """
        return math.sqrt(self._r ** 2 + self._z ** 2)

    def to_cartesian(self) -> tuple[float, float, float]:
        """Convert to Cartesian coordinates.

        Returns:
            Cartesian coordinates (x, y, z)

        Example:
            >>> x, y, z = coord.to_cartesian()
        """
        x = self._r * math.cos(self._theta)
        y = self._r * math.sin(self._theta)
        return (x, y, self._z)

    def to_spherical(self) -> tuple[float, float, float]:
        """Convert to spherical coordinates.

        Returns:
            Spherical coordinates (r, theta, phi)

        Example:
            >>> r, theta, phi = coord.to_spherical()
        """
        r = self.magnitude()
        theta = self._theta
        phi = math.atan2(self._r, self._z)
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
            >>> transformed = coord.transform_to("cartesian")
        """
        if target_system == "cylindrical":
            return self
        elif target_system == "cartesian":
            from quantsmind.scientific.coordinates.cartesian import CartesianCoordinate
            x, y, z = self.to_cartesian()
            return CartesianCoordinate(x, y, z)
        elif target_system == "spherical":
            from quantsmind.scientific.coordinates.spherical import SphericalCoordinate
            r, theta, phi = self.to_spherical()
            return SphericalCoordinate(r, theta, phi)
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
            "r": self._r,
            "theta": self._theta,
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
        return f"CylindricalCoordinate(r={self._r}, theta={self._theta}, z={self._z})"


# Export
__all__ = [
    "CylindricalCoordinate",
]
