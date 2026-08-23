"""
Knowledge Exceptions Module

This module provides the exception hierarchy for the Knowledge package.

Purpose
-------
Define domain-specific exceptions for knowledge management operations.

Responsibilities
----------------
- Define base knowledge exception
- Define dataset exceptions
- Define metadata exceptions
- Define ontology exceptions
- Define graph exceptions
- Define provenance exceptions
- Define reasoning exceptions
- Define repository exceptions
- Define validation exceptions
- Define serialization exceptions

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

from typing import Any


class KnowledgeError(Exception):
    """Base exception for all knowledge-related errors.

    This exception serves as the parent class for all knowledge package exceptions.

    Attributes:
        message: Error message
        context: Additional context information

    Example:
        >>> raise KnowledgeError("Knowledge operation failed")
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize a KnowledgeError.

        Args:
            message: Error message
            context: Additional context information

        Example:
            >>> raise KnowledgeError("Knowledge operation failed", {"operation": "save"})
        """
        self.message = message
        self.context = context or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> str(error)
        """
        if self.context:
            return f"{self.message} (Context: {self.context})"
        return self.message


class DatasetError(KnowledgeError):
    """Exception for dataset-related errors.

    Raised when dataset operations fail.

    Example:
        >>> raise DatasetError("Dataset not found", {"dataset_id": "ds_001"})
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize a DatasetError.

        Args:
            message: Error message
            context: Additional context information

        Example:
            >>> raise DatasetError("Dataset not found", {"dataset_id": "ds_001"})
        """
        super().__init__(message, context)


class MetadataError(KnowledgeError):
    """Exception for metadata-related errors.

    Raised when metadata operations fail.

    Example:
        >>> raise MetadataError("Invalid metadata format")
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize a MetadataError.

        Args:
            message: Error message
            context: Additional context information

        Example:
            >>> raise MetadataError("Invalid metadata format")
        """
        super().__init__(message, context)


class OntologyError(KnowledgeError):
    """Exception for ontology-related errors.

    Raised when ontology operations fail.

    Example:
        >>> raise OntologyError("Concept not found in ontology")
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize an OntologyError.

        Args:
            message: Error message
            context: Additional context information

        Example:
            >>> raise OntologyError("Concept not found in ontology")
        """
        super().__init__(message, context)


class GraphError(KnowledgeError):
    """Exception for graph-related errors.

    Raised when graph operations fail.

    Example:
        >>> raise GraphError("Graph traversal failed")
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize a GraphError.

        Args:
            message: Error message
            context: Additional context information

        Example:
            >>> raise GraphError("Graph traversal failed")
        """
        super().__init__(message, context)


class ProvenanceError(KnowledgeError):
    """Exception for provenance-related errors.

    Raised when provenance operations fail.

    Example:
        >>> raise ProvenanceError("Provenance chain broken")
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize a ProvenanceError.

        Args:
            message: Error message
            context: Additional context information

        Example:
            >>> raise ProvenanceError("Provenance chain broken")
        """
        super().__init__(message, context)


class ReasoningError(KnowledgeError):
    """Exception for reasoning-related errors.

    Raised when reasoning operations fail.

    Example:
        >>> raise ReasoningError("Inference failed")
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize a ReasoningError.

        Args:
            message: Error message
            context: Additional context information

        Example:
            >>> raise ReasoningError("Inference failed")
        """
        super().__init__(message, context)


class RepositoryError(KnowledgeError):
    """Exception for repository-related errors.

    Raised when repository operations fail.

    Example:
        >>> raise RepositoryError("Knowledge item not found")
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize a RepositoryError.

        Args:
            message: Error message
            context: Additional context information

        Example:
            >>> raise RepositoryError("Knowledge item not found")
        """
        super().__init__(message, context)


class ValidationError(KnowledgeError):
    """Exception for validation-related errors.

    Raised when validation operations fail.

    Example:
        >>> raise ValidationError("Schema validation failed")
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize a ValidationError.

        Args:
            message: Error message
            context: Additional context information

        Example:
            >>> raise ValidationError("Schema validation failed")
        """
        super().__init__(message, context)


class SerializationError(KnowledgeError):
    """Exception for serialization-related errors.

    Raised when serialization operations fail.

    Example:
        >>> raise SerializationError("JSON serialization failed")
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize a SerializationError.

        Args:
            message: Error message
            context: Additional context information

        Example:
            >>> raise SerializationError("JSON serialization failed")
        """
        super().__init__(message, context)


class SearchError(KnowledgeError):
    """Exception for search-related errors.

    Raised when search operations fail.

    Example:
        >>> raise SearchError("Search query invalid")
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize a SearchError.

        Args:
            message: Error message
            context: Additional context information

        Example:
            >>> raise SearchError("Search query invalid")
        """
        super().__init__(message, context)


class TransformationError(KnowledgeError):
    """Exception for transformation-related errors.

    Raised when transformation operations fail.

    Example:
        >>> raise TransformationError("Data transformation failed")
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize a TransformationError.

        Args:
            message: Error message
            context: Additional context information

        Example:
            >>> raise TransformationError("Data transformation failed")
        """
        super().__init__(message, context)


class EvidenceError(KnowledgeError):
    """Exception for evidence-related errors.

    Raised when evidence operations fail.

    Example:
        >>> raise EvidenceError("Evidence chain invalid")
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize an EvidenceError.

        Args:
            message: Error message
            context: Additional context information

        Example:
            >>> raise EvidenceError("Evidence chain invalid")
        """
        super().__init__(message, context)


class LineageError(KnowledgeError):
    """Exception for lineage-related errors.

    Raised when lineage operations fail.

    Example:
        >>> raise LineageError("Lineage tracking failed")
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize a LineageError.

        Args:
            message: Error message
            context: Additional context information

        Example:
            >>> raise LineageError("Lineage tracking failed")
        """
        super().__init__(message, context)


class QualityError(KnowledgeError):
    """Exception for quality-related errors.

    Raised when quality checks fail.

    Example:
        >>> raise QualityError("Quality rule violation")
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize a QualityError.

        Args:
            message: Error message
            context: Additional context information

        Example:
            >>> raise QualityError("Quality rule violation")
        """
        super().__init__(message, context)


class VersionError(KnowledgeError):
    """Exception for version-related errors.

    Raised when version operations fail.

    Example:
        >>> raise VersionError("Version conflict")
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize a VersionError.

        Args:
            message: Error message
            context: Additional context information

        Example:
            >>> raise VersionError("Version conflict")
        """
        super().__init__(message, context)


# Export
__all__ = [
    "KnowledgeError",
    "DatasetError",
    "MetadataError",
    "OntologyError",
    "GraphError",
    "ProvenanceError",
    "ReasoningError",
    "RepositoryError",
    "ValidationError",
    "SerializationError",
    "SearchError",
    "TransformationError",
    "EvidenceError",
    "LineageError",
    "QualityError",
    "VersionError",
]
