"""
Semantic Search Module

This module provides semantic search definitions for the Knowledge package.

Purpose
-------
Provide semantic search management for knowledge retrieval.

Responsibilities
----------------
- Define semantic search structure
- Support semantic search operations
- Support semantic search validation
- Support semantic search metadata

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.interfaces (knowledge interfaces)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.knowledge.enums import SearchType
from quantsmind.knowledge.exceptions import SearchError
from quantsmind.knowledge.interfaces import ISearchEngine
from quantsmind.knowledge.types import SearchResult, ValidationResult


class SemanticSearch(ISearchEngine):
    """Concrete implementation of a semantic search engine.

    This class provides semantic search functionality using embeddings.

    Attributes:
        _id: Search engine ID
        _name: Search engine name
        _search_type: Search type
        _embeddings: Entity embeddings
        _dimension: Embedding dimension
        _metadata: Search engine metadata

    Example:
        >>> search = SemanticSearch("sem_search_001", "Semantic Search", 128)
        >>> search.index_document("doc_001", {"embedding": [0.1, 0.2, 0.3]})
    """

    def __init__(
        self,
        search_id: str,
        name: str,
        dimension: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a SemanticSearch.

        Args:
            search_id: Search engine ID
            name: Search engine name
            dimension: Embedding dimension
            metadata: Search engine metadata

        Example:
            >>> search = SemanticSearch("sem_search_001", "Semantic Search", 128)
        """
        if not search_id:
            raise SearchError("Search ID cannot be empty", {"search_id": search_id})

        if not name:
            raise SearchError("Search name cannot be empty", {"name": name})

        if dimension <= 0:
            raise SearchError("Dimension must be positive", {"dimension": dimension})

        self._id = search_id
        self._name = name
        self._search_type = SearchType.SEMANTIC
        self._dimension = dimension
        self._embeddings: dict[str, list[float]] = {}
        self._documents: dict[str, dict[str, Any]] = {}
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the search engine ID.

        Returns:
            Search engine ID

        Example:
            >>> sid = search.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the search engine name.

        Returns:
            Search engine name

        Example:
            >>> name = search.name
        """
        return self._name

    @property
    def search_type(self) -> SearchType:
        """Get the search type.

        Returns:
            Search type

        Example:
            >>> stype = search.search_type
        """
        return self._search_type

    @property
    def dimension(self) -> int:
        """Get the embedding dimension.

        Returns:
            Embedding dimension

        Example:
            >>> dimension = search.dimension
        """
        return self._dimension

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the search engine metadata.

        Returns:
            Search engine metadata

        Example:
            >>> metadata = search.metadata
        """
        return self._metadata.copy()

    def index_document(self, doc_id: str, document: dict[str, Any]) -> None:
        """Index a document for semantic search.

        Args:
            doc_id: Document ID
            document: Document data with embedding

        Example:
            >>> search.index_document("doc_001", {"embedding": [0.1, 0.2, 0.3], "title": "Test"})
        """
        if "embedding" not in document:
            raise SearchError("Document must contain embedding", {"doc_id": doc_id})

        embedding = document["embedding"]
        if len(embedding) != self._dimension:
            raise SearchError(f"Embedding dimension mismatch: expected {self._dimension}, got {len(embedding)}", {"dimension": len(embedding)})

        self._embeddings[doc_id] = embedding
        self._documents[doc_id] = document

    def remove_document(self, doc_id: str) -> bool:
        """Remove a document from the index.

        Args:
            doc_id: Document ID

        Returns:
            True if removed

        Example:
            >>> removed = search.remove_document("doc_001")
        """
        if doc_id in self._embeddings:
            del self._embeddings[doc_id]
            del self._documents[doc_id]
            return True
        return False

    def search(self, query_embedding: list[float], top_k: int = 10) -> list[SearchResult]:
        """Search for similar documents.

        Args:
            query_embedding: Query embedding
            top_k: Number of results to return

        Returns:
            List of search results

        Example:
            >>> results = search.search([0.1, 0.2, 0.3], top_k=5)
        """
        if len(query_embedding) != self._dimension:
            raise SearchError(f"Query embedding dimension mismatch: expected {self._dimension}, got {len(query_embedding)}", {"dimension": len(query_embedding)})

        results = []

        for doc_id, embedding in self._embeddings.items():
            similarity = self._cosine_similarity(query_embedding, embedding)
            results.append(SearchResult(doc_id, similarity, self._documents[doc_id]))

        # Sort by similarity descending
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def _cosine_similarity(self, embedding1: list[float], embedding2: list[float]) -> float:
        """Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Cosine similarity

        Example:
            >>> similarity = search._cosine_similarity([0.1, 0.2], [0.1, 0.3])
        """
        if len(embedding1) != len(embedding2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(embedding1, embedding2, strict=False))
        magnitude1 = sum(a * a for a in embedding1) ** 0.5
        magnitude2 = sum(b * b for b in embedding2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def validate(self) -> ValidationResult:
        """Validate the semantic search.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = search.validate()
        """
        errors = []

        if not self._id:
            errors.append("Search ID cannot be empty")

        if not self._name:
            errors.append("Search name cannot be empty")

        if self._dimension <= 0:
            errors.append("Dimension must be positive")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Search engine definition

        Example:
            >>> data = search.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "search_type": self._search_type.value,
            "dimension": self._dimension,
            "document_count": len(self._embeddings),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(search)
        """
        return f"SemanticSearch(id={self._id}, name={self._name}, dimension={self._dimension}, documents={len(self._embeddings)})"


# Export
__all__ = [
    "SemanticSearch",
]
