"""
Space Module

This module provides coordinate/topological context for entities within the QuantsMind SDK.
Space represents the dimensional context in which entities exist (Euclidean, Hilbert, configuration space).

Purpose
-------
Provide coordinate/topological context for entities in the Foundation package.

Scientific Meaning
------------------
Space represents the dimensional context: Euclidean space (3D physical space),
Hilbert space (quantum state space), configuration space (all possible system configurations).

Responsibilities
----------------
- Manage space dimensions
- Support coordinate transformations
- Enable space serialization
- Handle space boundaries
- Support space queries

Dependencies
------------
typing (standard library)
logging (standard library)
quantsmind.foundation.exceptions (exception hierarchy)
quantsmind.foundation.constants (constant values)
quantsmind.foundation.types (type definitions)
quantsmind.foundation.enums (enumeration types)
quantsmind.foundation.interfaces (abstract interfaces)

Future Extensions
-----------------
- Curved space (Riemannian manifolds)
- Discrete space (lattices)
- Space-time manifolds
- Coordinate-free representations
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from quantsmind.foundation.constants import DEFAULT_DIMENSION, DEFAULT_SPACE_TYPE, MAX_DIMENSION, MIN_DIMENSION
from quantsmind.foundation.enums import SpaceType
from quantsmind.foundation.exceptions import (
    CoordinateError,
    DimensionError,
    InvalidSpaceError,
    SpaceError,
)
from quantsmind.foundation.interfaces import (
    Serializable,
    Validatable,
)
from quantsmind.foundation.types import (
    Coordinate,
    MetadataDict,
    SerializedData,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class Space(Serializable, Validatable):
    """Concrete implementation of coordinate/topological context.

    This class provides a flexible space representation with support for
    arbitrary dimensions, coordinate systems, and transformations.

    Scientific Meaning
    ------------------
    In scientific computing, space represents the dimensional context:
    Euclidean space (3D physical space), Hilbert space (quantum state space),
    configuration space (all possible system configurations).

    Attributes:
        _dimension: Number of dimensions
        _space_type: Type of space
        _origin: Origin coordinate
        _basis: Basis vectors
        _metadata: Additional metadata

    Example:
        >>> space = Space(dimension=3, space_type=SpaceType.EUCLIDEAN)
        >>> print(f"Dimension: {space.dimension}")
    """

    def __init__(
        self,
        dimension: int = DEFAULT_DIMENSION,
        space_type: SpaceType = SpaceType.EUCLIDEAN,
        origin: Optional[Coordinate] = None,
        basis: Optional[List[Coordinate]] = None,
        metadata: Optional[MetadataDict] = None,
    ) -> None:
        """Initialize a Space.

        Args:
            dimension: Number of dimensions
            space_type: Type of space
            origin: Optional origin coordinate
            basis: Optional basis vectors
            metadata: Optional metadata dictionary

        Raises:
            InvalidSpaceError: If dimension is invalid
            ValueError: If dimension out of range

        Example:
            >>> space = Space(dimension=3, space_type=SpaceType.EUCLIDEAN)
        """
        self._dimension: int = dimension
        self._space_type: SpaceType = space_type
        self._origin: Coordinate = origin or [0.0] * dimension
        self._basis: List[Coordinate] = basis or self._default_basis()
        self._metadata: MetadataDict = metadata or {}

        self._validate_dimension()
        logger.debug(f"Created {space_type.value} space with {dimension} dimensions")

    def _default_basis(self) -> List[Coordinate]:
        """Create default orthonormal basis.

        Returns:
            List of basis vectors
        """
        basis = []
        for i in range(self._dimension):
            vec = [0.0] * self._dimension
            vec[i] = 1.0
            basis.append(vec)
        return basis

    def _validate_dimension(self) -> None:
        """Validate the dimension.

        Raises:
            InvalidSpaceError: If dimension is invalid
            ValueError: If dimension out of range
        """
        if not isinstance(self._dimension, int) or self._dimension < MIN_DIMENSION:
            raise ValueError(f"Dimension must be >= {MIN_DIMENSION}")
        if self._dimension > MAX_DIMENSION:
            raise ValueError(f"Dimension must be <= {MAX_DIMENSION}")

    @property
    def dimension(self) -> int:
        """Get the space dimension.

        Returns:
            Number of dimensions

        Example:
            >>> print(f"Dimension: {space.dimension}")
        """
        return self._dimension

    @property
    def space_type(self) -> SpaceType:
        """Get the space type.

        Returns:
            Space type

        Example:
            >>> print(f"Type: {space.space_type}")
        """
        return self._space_type

    @property
    def origin(self) -> Coordinate:
        """Get the origin coordinate.

        Returns:
            Origin coordinate

        Example:
            >>> print(f"Origin: {space.origin}")
        """
        return self._origin.copy()

    @property
    def basis(self) -> List[Coordinate]:
        """Get the basis vectors.

        Returns:
            List of basis vectors

        Example:
            >>> print(f"Basis: {space.basis}")
        """
        return [vec.copy() for vec in self._basis]

    @property
    def metadata(self) -> MetadataDict:
        """Get the space metadata.

        Returns:
            Metadata dictionary

        Example:
            >>> print(f"Metadata: {space.metadata}")
        """
        return self._metadata.copy()

    def set_origin(self, origin: Coordinate) -> None:
        """Set the origin coordinate.

        Args:
            origin: New origin coordinate

        Raises:
            CoordinateError: If coordinate is invalid

        Example:
            >>> space.set_origin([1.0, 2.0, 3.0])
        """
        if len(origin) != self._dimension:
            raise CoordinateError(f"Coordinate must have {self._dimension} dimensions")
        self._origin = origin.copy()
        logger.debug(f"Updated space origin: {origin}")

    def set_basis(self, basis: List[Coordinate]) -> None:
        """Set the basis vectors.

        Args:
            basis: New basis vectors

        Raises:
            CoordinateError: If basis is invalid

        Example:
            >>> space.set_basis([[1.0, 0.0], [0.0, 1.0]])
        """
        if len(basis) != self._dimension:
            raise CoordinateError(f"Basis must have {self._dimension} vectors")
        for vec in basis:
            if len(vec) != self._dimension:
                raise CoordinateError(f"Basis vector must have {self._dimension} dimensions")
        self._basis = [vec.copy() for vec in basis]
        logger.debug(f"Updated space basis")

    # Validation methods
    def validate_coordinate(self, coordinate: Coordinate) -> bool:
        """Validate a coordinate.

        Args:
            coordinate: Coordinate to validate

        Returns:
            True if valid, False otherwise

        Example:
            >>> if space.validate_coordinate([1.0, 2.0, 3.0]):
            ...     print("Valid coordinate")
        """
        return isinstance(coordinate, list) and len(coordinate) == self._dimension

    # Serializable interface implementation
    def serialize(self, format: str = "json") -> bytes:
        """Serialize the space to bytes.

        Args:
            format: Serialization format (currently only "json" supported)

        Returns:
            Serialized data as bytes

        Raises:
            NotImplementedError: If format is not supported

        Example:
            >>> data = space.serialize(format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        data = {
            "dimension": self._dimension,
            "space_type": self._space_type.value,
            "origin": self._origin,
            "basis": self._basis,
            "metadata": self._metadata,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes, format: str = "json") -> "Space":
        """Deserialize the space from bytes.

        Args:
            data: Serialized data as bytes
            format: Serialization format (currently only "json" supported)

        Returns:
            Deserialized Space instance

        Raises:
            NotImplementedError: If format is not supported
            InvalidSpaceError: If data is invalid

        Example:
            >>> space = Space.deserialize(data, format="json")
        """
        if format != "json":
            raise NotImplementedError(f"Serialization format '{format}' not yet implemented")

        import json

        try:
            obj = json.loads(data.decode("utf-8"))
            return cls(
                dimension=obj["dimension"],
                space_type=SpaceType(obj["space_type"]),
                origin=obj.get("origin"),
                basis=obj.get("basis"),
                metadata=obj.get("metadata"),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise InvalidSpaceError(f"Failed to deserialize space: {e}") from e

    def is_serializable(self) -> bool:
        """Check if the space is serializable.

        Returns:
            True (spaces are always serializable)

        Example:
            >>> if space.is_serializable():
            ...     data = space.serialize()
        """
        return True

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get supported serialization formats.

        Returns:
            List of supported formats

        Example:
            >>> formats = Space.get_supported_formats()
        """
        return ["json"]

    # Validatable interface implementation
    def validate(self) -> ValidationResult:
        """Validate the space.

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> is_valid, errors = space.validate()
        """
        errors: list[str] = []

        try:
            self._validate_dimension()
        except (InvalidSpaceError, ValueError) as e:
            errors.append(str(e))

        if len(self._origin) != self._dimension:
            errors.append(f"Origin must have {self._dimension} dimensions")

        if len(self._basis) != self._dimension:
            errors.append(f"Basis must have {self._dimension} vectors")

        return (len(errors) == 0, errors)

    @property
    def validation_errors(self) -> list[str]:
        """Get validation errors.

        Returns:
            List of error messages

        Example:
            >>> errors = space.validation_errors
        """
        is_valid, errors = self.validate()
        return errors if not is_valid else []

    @property
    def validation_warnings(self) -> list[str]:
        """Get validation warnings.

        Returns:
            List of warning messages (currently empty)

        Example:
            >>> warnings = space.validation_warnings
        """
        return []

    # Object protocol methods
    def __repr__(self) -> str:
        """Return string representation of the space.

        Returns:
            String representation

        Example:
            >>> repr(space)
        """
        return f"Space(dimension={self._dimension}, type={self._space_type.value})"

    def __str__(self) -> str:
        """Return string representation of the space.

        Returns:
            String representation

        Example:
            >>> str(space)
        """
        return f"{self._space_type.value} space ({self._dimension}D)"

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> space1 == space2
        """
        if not isinstance(other, Space):
            return False
        return (
            self._dimension == other._dimension
            and self._space_type == other._space_type
        )

    def __hash__(self) -> int:
        """Return hash of the space.

        Returns:
            Hash value

        Example:
            >>> hash(space)
        """
        return hash((self._dimension, self._space_type))


# Export
__all__ = ["Space"]
