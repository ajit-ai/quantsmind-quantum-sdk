"""
Vector Module

This module provides vector operations for the Mathematics package.
Vector represents a mathematical vector with support for common operations.

Purpose
-------
Provide vector operations for the Mathematics package.

Scientific Meaning
------------------
Vector represents a mathematical vector: position, velocity, force, momentum,
quantum state vector, or any other vector quantity in scientific computing.

Responsibilities
----------------
- Support vector creation
- Enable vector operations
- Support vector transformations
- Handle vector validation

Dependencies
------------
math (standard library)
typing (standard library)
quantsmind.math.exceptions (exception hierarchy)
quantsmind.math.types (type definitions)
quantsmind.math.utilities (utility functions)
quantsmind.math.validation (validation functions)

Future Extensions
-----------------
- GPU-accelerated operations
- Sparse vectors
- Complex vector operations
- Vector views
"""

from __future__ import annotations

import logging
from typing import Any

from quantsmind.math.exceptions import (
    DimensionError,
    DivisionByZeroError,
)
from quantsmind.math.exceptions import (
    IndexError as MathIndexError,
)
from quantsmind.math.types import Scalar
from quantsmind.math.utilities import (
    angle_between,
    distance,
    dot_product,
    magnitude,
    project,
)
from quantsmind.math.validation import validate_vector

logger = logging.getLogger(__name__)


class Vector:
    """Concrete implementation of a mathematical vector.

    This class provides a comprehensive vector representation with support for
    common vector operations including addition, subtraction, multiplication,
    dot product, cross product, and normalization.

    Scientific Meaning
    ------------------
    In scientific computing, vectors represent quantities with both magnitude
    and direction: position, velocity, force, momentum, quantum state vectors.

    Attributes:
        _data: Vector data
        _dimension: Vector dimension

    Example:
        >>> v = Vector([1.0, 2.0, 3.0])
        >>> print(f"Magnitude: {v.magnitude()}")
    """

    def __init__(self, data: list[Scalar]) -> None:
        """Initialize a Vector.

        Args:
            data: Vector data as list of scalars

        Raises:
            ValueError: If data is invalid

        Example:
            >>> v = Vector([1.0, 2.0, 3.0])
        """
        is_valid, errors = validate_vector(data)
        if not is_valid:
            raise ValueError(f"Invalid vector data: {errors}")

        self._data: list[Scalar] = list(data)
        self._dimension: int = len(self._data)
        logger.debug(f"Created vector of dimension {self._dimension}")

    @property
    def dimension(self) -> int:
        """Get the vector dimension.

        Returns:
            Vector dimension

        Example:
            >>> print(f"Dimension: {vector.dimension}")
        """
        return self._dimension

    @property
    def data(self) -> list[Scalar]:
        """Get the vector data.

        Returns:
            Vector data

        Example:
            >>> print(f"Data: {vector.data}")
        """
        return self._data.copy()

    def __getitem__(self, index: int) -> Scalar:
        """Get vector element by index.

        Args:
            index: Element index

        Returns:
            Element value

        Raises:
            IndexError: If index is out of bounds

        Example:
            >>> value = vector[0]
        """
        if index < 0 or index >= self._dimension:
            raise MathIndexError(f"Index {index} out of bounds for dimension {self._dimension}")
        return self._data[index]

    def __setitem__(self, index: int, value: Scalar) -> None:
        """Set vector element by index.

        Args:
            index: Element index
            value: Element value

        Raises:
            IndexError: If index is out of bounds

        Example:
            >>> vector[0] = 5.0
        """
        if index < 0 or index >= self._dimension:
            raise MathIndexError(f"Index {index} out of bounds for dimension {self._dimension}")
        self._data[index] = value

    def __len__(self) -> int:
        """Get vector length.

        Returns:
            Vector dimension

        Example:
            >>> len(vector)
        """
        return self._dimension

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(vector)
        """
        return f"Vector({self._data})"

    def __str__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> str(vector)
        """
        return f"[{', '.join(str(x) for x in self._data)}]"

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> vector1 == vector2
        """
        if not isinstance(other, Vector):
            return False
        if self._dimension != other._dimension:
            return False
        return all(abs(a - b) < 1e-10 for a, b in zip(self._data, other._data, strict=False))

    def __hash__(self) -> int:
        """Return hash.

        Returns:
            Hash value

        Example:
            >>> hash(vector)
        """
        return hash(tuple(self._data))

    def __add__(self, other: Vector) -> Vector:
        """Add two vectors.

        Args:
            other: Other vector

        Returns:
            Sum vector

        Raises:
            DimensionError: If dimensions don't match

        Example:
            >>> result = vector1 + vector2
        """
        if self._dimension != other._dimension:
            raise DimensionError(f"Dimension mismatch: {self._dimension} vs {other._dimension}")
        return Vector([a + b for a, b in zip(self._data, other._data, strict=False)])

    def __sub__(self, other: Vector) -> Vector:
        """Subtract two vectors.

        Args:
            other: Other vector

        Returns:
            Difference vector

        Raises:
            DimensionError: If dimensions don't match

        Example:
            >>> result = vector1 - vector2
        """
        if self._dimension != other._dimension:
            raise DimensionError(f"Dimension mismatch: {self._dimension} vs {other._dimension}")
        return Vector([a - b for a, b in zip(self._data, other._data, strict=False)])

    def __mul__(self, scalar: Scalar) -> Vector:
        """Multiply vector by scalar.

        Args:
            scalar: Scalar value

        Returns:
            Scaled vector

        Example:
            >>> result = vector * 2.0
        """
        return Vector([x * scalar for x in self._data])

    def __rmul__(self, scalar: Scalar) -> Vector:
        """Multiply scalar by vector.

        Args:
            scalar: Scalar value

        Returns:
            Scaled vector

        Example:
            >>> result = 2.0 * vector
        """
        return self.__mul__(scalar)

    def __truediv__(self, scalar: Scalar) -> Vector:
        """Divide vector by scalar.

        Args:
            scalar: Scalar value

        Returns:
            Scaled vector

        Raises:
            DivisionByZeroError: If scalar is zero

        Example:
            >>> result = vector / 2.0
        """
        if scalar == 0:
            raise DivisionByZeroError("Cannot divide by zero")
        return Vector([x / scalar for x in self._data])

    def magnitude(self) -> float:
        """Calculate vector magnitude.

        Returns:
            Vector magnitude

        Example:
            >>> mag = vector.magnitude()
        """
        return magnitude(self._data)

    def normalize(self) -> Vector:
        """Normalize vector to unit length.

        Returns:
            Normalized vector

        Raises:
            DivisionByZeroError: If vector has zero magnitude

        Example:
            >>> normalized = vector.normalize()
        """
        mag = self.magnitude()
        if mag == 0:
            raise DivisionByZeroError("Cannot normalize zero vector")
        return Vector([x / mag for x in self._data])

    def dot(self, other: Vector) -> float:
        """Calculate dot product with another vector.

        Args:
            other: Other vector

        Returns:
            Dot product

        Raises:
            DimensionError: If dimensions don't match

        Example:
            >>> dot = vector1.dot(vector2)
        """
        if self._dimension != other._dimension:
            raise DimensionError(f"Dimension mismatch: {self._dimension} vs {other._dimension}")
        return dot_product(self._data, other._data)

    def cross(self, other: Vector) -> Vector:
        """Calculate cross product with another vector (3D only).

        Args:
            other: Other vector

        Returns:
            Cross product vector

        Raises:
            DimensionError: If vectors are not 3D

        Example:
            >>> cross = vector1.cross(vector2)
        """
        if self._dimension != 3 or other._dimension != 3:
            raise DimensionError("Cross product requires 3D vectors")
        
        return Vector([
            self._data[1] * other._data[2] - self._data[2] * other._data[1],
            self._data[2] * other._data[0] - self._data[0] * other._data[2],
            self._data[0] * other._data[1] - self._data[1] * other._data[0],
        ])

    def distance_to(self, other: Vector) -> float:
        """Calculate Euclidean distance to another vector.

        Args:
            other: Other vector

        Returns:
            Euclidean distance

        Raises:
            DimensionError: If dimensions don't match

        Example:
            >>> dist = vector1.distance_to(vector2)
        """
        if self._dimension != other._dimension:
            raise DimensionError(f"Dimension mismatch: {self._dimension} vs {other._dimension}")
        return distance(self._data, other._data)

    def angle_with(self, other: Vector) -> float:
        """Calculate angle with another vector in radians.

        Args:
            other: Other vector

        Returns:
            Angle in radians

        Raises:
            DimensionError: If dimensions don't match
            DivisionByZeroError: If either vector has zero magnitude

        Example:
            >>> angle = vector1.angle_with(vector2)
        """
        if self._dimension != other._dimension:
            raise DimensionError(f"Dimension mismatch: {self._dimension} vs {other._dimension}")
        return angle_between(self._data, other._data)

    def project_onto(self, other: Vector) -> Vector:
        """Project this vector onto another vector.

        Args:
            other: Vector to project onto

        Returns:
            Projected vector

        Raises:
            DimensionError: If dimensions don't match
            DivisionByZeroError: If other vector has zero magnitude

        Example:
            >>> projected = vector1.project_onto(vector2)
        """
        if self._dimension != other._dimension:
            raise DimensionError(f"Dimension mismatch: {self._dimension} vs {other._dimension}")
        return Vector(project(self._data, other._data))

    def to_list(self) -> list[Scalar]:
        """Convert vector to list.

        Returns:
            List representation

        Example:
            >>> data = vector.to_list()
        """
        return self._data.copy()

    def copy(self) -> Vector:
        """Create a copy of the vector.

        Returns:
            Copy of vector

        Example:
            >>> copy = vector.copy()
        """
        return Vector(self._data.copy())


class BasisVector(Vector):
    """A vector that forms part of a basis.

    This class represents a basis vector, typically a unit vector along
    a coordinate axis.

    Example:
        >>> e1 = BasisVector([1.0, 0.0, 0.0])
    """

    def __init__(self, data: list[Scalar], index: int = 0) -> None:
        """Initialize a BasisVector.

        Args:
            data: Vector data
            index: Basis index

        Example:
            >>> e1 = BasisVector([1.0, 0.0, 0.0], index=0)
        """
        super().__init__(data)
        self._index = index

    @property
    def index(self) -> int:
        """Get the basis index.

        Returns:
            Basis index

        Example:
            >>> print(f"Index: {basis_vector.index}")
        """
        return self._index


class UnitVector(Vector):
    """A vector with unit magnitude.

    This class represents a unit vector (magnitude = 1).

    Example:
        >>> u = UnitVector([1.0, 0.0, 0.0])
    """

    def __init__(self, data: list[Scalar]) -> None:
        """Initialize a UnitVector.

        Args:
            data: Vector data (will be normalized)

        Example:
            >>> u = UnitVector([1.0, 0.0, 0.0])
        """
        super().__init__(data)
        self.normalize_in_place()

    def normalize_in_place(self) -> None:
        """Normalize the vector in place.

        Raises:
            DivisionByZeroError: If vector has zero magnitude

        Example:
            >>> unit_vector.normalize_in_place()
        """
        mag = self.magnitude()
        if mag == 0:
            raise DivisionByZeroError("Cannot normalize zero vector")
        self._data = [x / mag for x in self._data]


class CoordinateVector(Vector):
    """A vector representing coordinates in a coordinate system.

    This class represents a coordinate vector, typically used to represent
    positions in a coordinate system.

    Example:
        >>> coord = CoordinateVector([1.0, 2.0, 3.0])
    """

    def __init__(self, data: list[Scalar], coordinate_system: str = "cartesian") -> None:
        """Initialize a CoordinateVector.

        Args:
            data: Vector data
            coordinate_system: Coordinate system name

        Example:
            >>> coord = CoordinateVector([1.0, 2.0, 3.0], "cartesian")
        """
        super().__init__(data)
        self._coordinate_system = coordinate_system

    @property
    def coordinate_system(self) -> str:
        """Get the coordinate system.

        Returns:
            Coordinate system name

        Example:
            >>> print(f"Coordinate system: {coord.coordinate_system}")
        """
        return self._coordinate_system


# Export
__all__ = [
    "Vector",
    "BasisVector",
    "UnitVector",
    "CoordinateVector",
]
