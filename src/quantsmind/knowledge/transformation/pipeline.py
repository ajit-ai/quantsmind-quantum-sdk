"""
Pipeline Module

This module provides pipeline definitions for the Knowledge package.

Purpose
-------
Provide pipeline management for chaining transformations.

Responsibilities
----------------
- Define pipeline structure
- Support pipeline operations
- Support pipeline validation
- Support pipeline metadata

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.knowledge.exceptions import TransformationError
from quantsmind.knowledge.types import ValidationResult


class Pipeline:
    """Concrete implementation of a transformation pipeline.

    This class provides pipeline functionality for chaining transformations.

    Attributes:
        _id: Pipeline ID
        _name: Pipeline name
        _transformations: Transformations in the pipeline
        _metadata: Pipeline metadata

    Example:
        >>> pipeline = Pipeline("pipeline_001", "Data Processing")
        >>> pipeline.add_transformation(transformation)
    """

    def __init__(
        self,
        pipeline_id: str,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Pipeline.

        Args:
            pipeline_id: Pipeline ID
            name: Pipeline name
            metadata: Pipeline metadata

        Example:
            >>> pipeline = Pipeline("pipeline_001", "Data Processing")
        """
        if not pipeline_id:
            raise TransformationError("Pipeline ID cannot be empty", {"pipeline_id": pipeline_id})

        if not name:
            raise TransformationError("Pipeline name cannot be empty", {"name": name})

        self._id = pipeline_id
        self._name = name
        self._transformations: list[Any] = []
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the pipeline ID.

        Returns:
            Pipeline ID

        Example:
            >>> pid = pipeline.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the pipeline name.

        Returns:
            Pipeline name

        Example:
            >>> name = pipeline.name
        """
        return self._name

    @property
    def transformations(self) -> list[Any]:
        """Get the transformations.

        Returns:
            List of transformations

        Example:
            >>> transformations = pipeline.transformations
        """
        return self._transformations.copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the pipeline metadata.

        Returns:
            Pipeline metadata

        Example:
            >>> metadata = pipeline.metadata
        """
        return self._metadata.copy()

    def add_transformation(self, transformation: Any) -> None:
        """Add a transformation to the pipeline.

        Args:
            transformation: Transformation to add

        Example:
            >>> pipeline.add_transformation(transformation)
        """
        self._transformations.append(transformation)

    def remove_transformation(self, transformation_id: str) -> bool:
        """Remove a transformation from the pipeline.

        Args:
            transformation_id: Transformation ID

        Returns:
            True if removed

        Example:
            >>> removed = pipeline.remove_transformation("trans_001")
        """
        for i, trans in enumerate(self._transformations):
            if getattr(trans, 'id', None) == transformation_id:
                del self._transformations[i]
                return True
        return False

    def get_transformation(self, transformation_id: str) -> Any | None:
        """Get a transformation by ID.

        Args:
            transformation_id: Transformation ID

        Returns:
            Transformation or None

        Example:
            >>> transformation = pipeline.get_transformation("trans_001")
        """
        for trans in self._transformations:
            if getattr(trans, 'id', None) == transformation_id:
                return trans
        return None

    def execute(self, data: Any) -> Any:
        """Execute the pipeline on data.

        Args:
            data: Data to transform

        Returns:
            Transformed data

        Example:
            >>> result = pipeline.execute({"value": 42})
        """
        result = data
        for transformation in self._transformations:
            try:
                result = transformation.apply(result)
            except Exception as e:
                raise TransformationError(f"Pipeline step failed: {str(e)}", {"pipeline_id": self._id})

        return result

    def validate(self) -> ValidationResult:
        """Validate the pipeline.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = pipeline.validate()
        """
        errors = []

        if not self._id:
            errors.append("Pipeline ID cannot be empty")

        if not self._name:
            errors.append("Pipeline name cannot be empty")

        # Validate each transformation
        for transformation in self._transformations:
            if hasattr(transformation, 'validate'):
                valid, trans_errors = transformation.validate()
                errors.extend(trans_errors)

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Pipeline definition

        Example:
            >>> data = pipeline.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "transformation_count": len(self._transformations),
            "transformations": [getattr(t, 'id', str(i)) for i, t in enumerate(self._transformations)],
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(pipeline)
        """
        return f"Pipeline(id={self._id}, name={self._name}, transformations={len(self._transformations)})"


# Export
__all__ = [
    "Pipeline",
]
