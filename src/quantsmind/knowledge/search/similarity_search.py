"""
Similarity Search Module

This module provides similarity search definitions for the Knowledge package.

Purpose
-------
Provide similarity search management for knowledge retrieval.

Responsibilities
----------------
- Define similarity search structure
- Support similarity search operations
- Support similarity search validation
- Support similarity search metadata

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.interfaces (knowledge interfaces)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from quantsmind.knowledge.enums import SearchType
from quantsmind.knowledge.exceptions import SearchError
from quantsmind.knowledge.interfaces import ISearchEngine
from quantsmind.knowledge.types import SearchResult, ValidationResult


class SimilaritySearch(ISearchEngine):
    """Concrete implementation of a similarity search engine.

    This class provides similarity search functionality using custom similarity functions.

    Attributes:
        _id: Search engine ID
        _name: Search engine name
        _search_type: Search type
        _similarity_function: Similarity function
        _documents: Indexed documents
        _metadata: Search engine metadata

    Example:
        >>> sim_search = SimilaritySearch("sim_search_001", "Similarity Search")
        >>> sim_search.set_similarity_function(lambda a, b: 1.0 if a == b else 0.0)
    """

    def __init__(
        self,
        search_id: str,
        name: str,
        similarity_function: Callable[[Any, Any], float] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a SimilaritySearch.

        Args:
            search_id: Search engine ID
            name: Search engine name
            similarity_function: Similarity function
            metadata: Search engine metadata

        Example:
            >>> sim_search = SimilaritySearch("sim_search_001", "Similarity Search")
        """
        if not search_id:
            raise SearchError("Search ID cannot be empty", {"search_id": search_id})

        if not name:
            raise SearchError("Search name cannot be empty", {"name": name})

        self._id = search_id
        self._name = name
        self._search_type = SearchType.SIMILARITY
        self._similarity_function = similarity_function
        self._documents: dict[str, dict[str, Any]] = {}
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the search engine ID.

        Returns:
            Search engine ID

        Example:
            >>> sid = sim_search.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the search engine name.

        Returns:
            Search engine name

        Example:
            >>> name = sim_search.name
        """
        return self._name

    @property
    def search_type(self) -> SearchType:
        """Get the search type.

        Returns:
            Search type

        Example:
            >>> stype = sim_search.search_type
        """
        return self._search_type

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the search engine metadata.

        Returns:
            Search engine metadata

        Example:
            >>> metadata = sim_search.metadata
        """
        return self._metadata.copy()

    def set_similarity_function(self, similarity_function: Callable[[Any, Any], float]) -> None:
        """Set the similarity function.

        Args:
            similarity_function: Similarity function

        Example:
            >>> sim_search.set_similarity_function(lambda a, b: 1.0 if a == b else 0.0)
        """
        self._similarity_function = similarity_function

    def index_document(self, doc_id: str, document: dict[str, Any]) -> None:
        """Index a document for similarity search.

        Args:
            doc_id: Document ID
            document: Document data

        Example:
            >>> sim_search.index_document("doc_001", {"value": 42})
        """
        self._documents[doc_id] = document

    def remove_document(self, doc_id: str) -> bool:
        """Remove a document from the index.

        Args:
            doc_id: Document ID

        Returns:
            True if removed

        Example:
            >>> removed = sim_search.remove_document("doc_001")
        """
        if doc_id in self._documents:
            del self._documents[doc_id]
            return True
        return False

    def search(self, query: Any, top_k: int = 10) -> list[SearchResult]:
        """Search for similar documents.

        Args:
            query: Query object
            top_k: Number of results to return

        Returns:
            List of search results

        Example:
            >>> results = sim_search.search({"value": 42}, top_k=5)
        """
        if not self._similarity_function:
            raise SearchError("Similarity function not set", {"search_id": self._id})

        results = []

        for doc_id, document in self._documents.items():
            try:
                similarity = self._similarity_function(query, document)
                results.append(SearchResult(doc_id, similarity, document))
            except Exception:
                # Skip documents that cause errors in similarity calculation
                continue

        # Sort by similarity descending
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def search_by_field(self, query: Any, field: str, top_k: int = 10) -> list[SearchResult]:
        """Search for similar documents by a specific field.

        Args:
            query: Query object
            field: Field to compare
            top_k: Number of results to return

        Returns:
            List of search results

        Example:
            >>> results = sim_search.search_by_field(42, "value", top_k=5)
        """
        if not self._similarity_function:
            raise SearchError("Similarity function not set", {"search_id": self._id})

        results = []

        for doc_id, document in self._documents.items():
            if field not in document:
                continue

            try:
                similarity = self._similarity_function(query, document[field])
                results.append(SearchResult(doc_id, similarity, document))
            except Exception:
                # Skip documents that cause errors in similarity calculation
                continue

        # Sort by similarity descending
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def validate(self) -> ValidationResult:
        """Validate the similarity search.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = sim_search.validate()
        """
        errors = []

        if not self._id:
            errors.append("Search ID cannot be empty")

        if not self._name:
            errors.append("Search name cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Search engine definition

        Example:
            >>> data = sim_search.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "search_type": self._search_type.value,
            "document_count": len(self._documents),
            "has_similarity_function": self._similarity_function is not None,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(sim_search)
        """
        return f"SimilaritySearch(id={self._id}, name={self._name}, documents={len(self._documents)})"


# Export
__all__ = [
    "SimilaritySearch",
]
