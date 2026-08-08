"""
Spherical Coordinate Module

This module provides spherical coordinate definitions for the Scientific package.

Purpose
-------
Provide spherical coordinate system implementation.

Responsibilities
----------------
- Define spherical coordinates
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
from typing import Any, Dict, Optional, Tuple

from quantsmind.scientific.exceptions import CoordinateError
from quantsmind.scientific.interfaces import ICoordinate
from quantsmind.scientific.types import CoordinateTriple, CoordinateValue


class SphericalCoordinate(ICoordinate):
    """Concrete implementation of spherical coordinates.

    This class provides spherical coordinate functionality.

    Attributes:
        _r: Radial distance
        _theta: Azimuthal angle (radians)
        _phi: Polar angle (radians)
        _metadata: Coordinate metadata

    Example:
        >>> coord = SphericalCoordinate(1.0, math.pi/4, math.pi/4)
        >>> coord.coordinates()
    """

    def __init__(
        self,
        r: CoordinateValue,
        theta: CoordinateValue,
        phi: CoordinateValue,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a SphericalCoordinate.

        Args:
            r: Radial distance
            theta: Azimuthal angle (radians)
            phi: Polar angle (radians)
            metadata: Coordinate metadata

        Example:
            >>> coord = SphericalCoordinate(1.0, math.pi/4, math.pi/4)
        """
        if r < 0:
            raise CoordinateError("Radial distance cannot be negative", coordinate="r")

        self._r = r
        self._theta = theta
        self._phi = phi
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
        """Get the azimuthal angle.

        Returns:
            Azimuthal angle (radians)

        Example:
            >>> print(f"Theta: {coord.theta}")
        """
        return self._theta

    @property
    def phi(self) -> CoordinateValue:
        """Get the polar angle.

        Returns:
            Polar angle (radians)

        Example:
            >>> print(f"Phi: {coord.phi}")
        """
        return self._phi

    @property
    def metadata(self) -> Dict[str, Any]:
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
            Coordinate values (r, theta, phi)

        Example:
            >>> coords = coord.coordinates()
        """
        return (self._r, self._theta, self._phi)

    def system(self) -> str:
        """Get the coordinate system.

        Returns:
            Coordinate system name

        Example:
            >>> print(f"System: {coord.system()}")
        """
        return "spherical"

    def magnitude(self) -> float:
        """Calculate the magnitude.

        Returns:
            Magnitude (radial distance)

        Example:
            >>> mag = coord.magnitude()
        """
        return self._r

    def to_cartesian(self) -> Tuple[float, float, float]:
        """Convert to Cartesian coordinates.

        Returns:
            Cartesian coordinates (x, y, z)

        Example:
            >>> x, y, z = coord.to_cartesian()
        """
        x = self._r * math.sin(self._phi) * math.cos(self._theta)
        y = self._r * math.sin(self._phi) * math.sin(self._theta)
        z = self._r * math.cos(self._phi)
        return (x, y, z)

    def to_cylindrical(self) -> Tuple[float, float, float]:
        """Convert to cylindrical coordinates.

        Returns:
            Cylindrical coordinates (r, theta, z)

        Example:
            >>> r, theta, z = coord.to_cylindrical()
        """
        r = self._r * math.sin(self._phi)
        theta = self._theta
        z = self._r * math.cos(self._phi)
        return (r, theta, z)

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
        if target_system == "spherical":
            return self
        elif target_system == "cartesian":
            from quantsmind.scientific.coordinates.cartesian import CartesianCoordinate
            x, y, z = self.to_cartesian()
            return CartesianCoordinate(x, y, z)
        elif target_system == "cylindrical":
            from quantsmind.scientific.coordinates.cylindrical import CylindricalCoordinate
            r, theta, z = self.to_cylindrical()
            return CylindricalCoordinate(r, theta, z)
        else:
            raise CoordinateError(f"Transformation to {target_system} not supported")

    def to_dict(self) -> Dict[str, Any]:
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
            "phi": self._phi,
            "metadata": self._metadata.copy(),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(coord)
        """
        return f"SphericalCoordinate(r={self._r}, theta={self._theta}, phi={self._phi})"


# Export
__all__ = [
    "SphericalCoordinate",
]
