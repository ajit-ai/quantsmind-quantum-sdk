"""
Semantic Index Module

This module provides semantic index definitions for the Knowledge package.

Purpose
-------
Provide semantic index management for semantic search.

Responsibilities
----------------
- Define semantic index structure
- Support semantic index operations
- Support semantic index validation
- Support semantic index metadata

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.knowledge.enums import IndexType
from quantsmind.knowledge.exceptions import IndexError
from quantsmind.knowledge.types import ValidationResult


class SemanticIndex:
    """Concrete implementation of a semantic index.

    This class provides semantic index functionality for semantic search.

    Attributes:
        _id: Index ID
        _name: Index name
        _index_type: Index type
        _embeddings: Entity embeddings
        _metadata: Index metadata

    Example:
        >>> semantic_index = SemanticIndex("sem_idx_001", "embedding_index", IndexType.SEMANTIC)
        >>> semantic_index.add("entity_001", [0.1, 0.2, 0.3])
    """

    def __init__(
        self,
        index_id: str,
        name: str,
        index_type: IndexType,
        dimension: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a SemanticIndex.

        Args:
            index_id: Index ID
            name: Index name
            index_type: Index type
            dimension: Embedding dimension
            metadata: Index metadata

        Example:
            >>> semantic_index = SemanticIndex("sem_idx_001", "embedding_index", IndexType.SEMANTIC, 128)
        """
        if not index_id:
            raise IndexError("Index ID cannot be empty", {"index_id": index_id})

        if not name:
            raise IndexError("Index name cannot be empty", {"name": name})

        if dimension <= 0:
            raise IndexError("Dimension must be positive", {"dimension": dimension})

        self._id = index_id
        self._name = name
        self._index_type = index_type
        self._dimension = dimension
        self._embeddings: Dict[str, List[float]] = {}
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the index ID.

        Returns:
            Index ID

        Example:
            >>> sid = semantic_index.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the index name.

        Returns:
            Index name

        Example:
            >>> name = semantic_index.name
        """
        return self._name

    @property
    def index_type(self) -> IndexType:
        """Get the index type.

        Returns:
            Index type

        Example:
            >>> itype = semantic_index.index_type
        """
        return self._index_type

    @property
    def dimension(self) -> int:
        """Get the embedding dimension.

        Returns:
            Embedding dimension

        Example:
            >>> dimension = semantic_index.dimension
        """
        return self._dimension

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the index metadata.

        Returns:
            Index metadata

        Example:
            >>> metadata = semantic_index.metadata
        """
        return self._metadata.copy()

    def add(self, entity_id: str, embedding: List[float]) -> None:
        """Add an entity embedding to the index.

        Args:
            entity_id: Entity ID
            embedding: Entity embedding

        Example:
            >>> semantic_index.add("entity_001", [0.1, 0.2, 0.3])
        """
        if len(embedding) != self._dimension:
            raise IndexError(f"Embedding dimension mismatch: expected {self._dimension}, got {len(embedding)}", {"dimension": len(embedding)})

        self._embeddings[entity_id] = embedding

    def remove(self, entity_id: str) -> bool:
        """Remove an entity from the index.

        Args:
            entity_id: Entity ID

        Returns:
            True if removed

        Example:
            >>> removed = semantic_index.remove("entity_001")
        """
        if entity_id in self._embeddings:
            del self._embeddings[entity_id]
            return True
        return False

    def get(self, entity_id: str) -> Optional[List[float]]:
        """Get an entity embedding.

        Args:
            entity_id: Entity ID

        Returns:
            Embedding or None

        Example:
            >>> embedding = semantic_index.get("entity_001")
        """
        return self._embeddings.get(entity_id)

    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Cosine similarity

        Example:
            >>> similarity = semantic_index.cosine_similarity([0.1, 0.2], [0.1, 0.3])
        """
        if len(embedding1) != len(embedding2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        magnitude1 = sum(a * a for a in embedding1) ** 0.5
        magnitude2 = sum(b * b for b in embedding2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def search(self, query_embedding: List[float], top_k: int = 10) -> List[tuple[str, float]]:
        """Search for similar entities.

        Args:
            query_embedding: Query embedding
            top_k: Number of results to return

        Returns:
            List of (entity_id, similarity) tuples

        Example:
            >>> results = semantic_index.search([0.1, 0.2, 0.3], top_k=5)
        """
        if len(query_embedding) != self._dimension:
            raise IndexError(f"Query embedding dimension mismatch: expected {self._dimension}, got {len(query_embedding)}", {"dimension": len(query_embedding)})

        similarities = []
        for entity_id, embedding in self._embeddings.items():
            similarity = self.cosine_similarity(query_embedding, embedding)
            similarities.append((entity_id, similarity))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def count(self) -> int:
        """Get the number of indexed entities.

        Returns:
            Number of entities

        Example:
            >>> count = semantic_index.count()
        """
        return len(self._embeddings)

    def validate(self) -> ValidationResult:
        """Validate the semantic index.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = semantic_index.validate()
        """
        errors = []

        if not self._id:
            errors.append("Index ID cannot be empty")

        if not self._name:
            errors.append("Index name cannot be empty")

        if self._dimension <= 0:
            errors.append("Dimension must be positive")

        # Validate all embeddings have correct dimension
        for entity_id, embedding in self._embeddings.items():
            if len(embedding) != self._dimension:
                errors.append(f"Entity '{entity_id}' has invalid embedding dimension")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Index definition

        Example:
            >>> data = semantic_index.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "index_type": self._index_type.value,
            "dimension": self._dimension,
            "entity_count": len(self._embeddings),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(semantic_index)
        """
        return f"SemanticIndex(id={self._id}, name={self._name}, type={self._index_type.value}, dimension={self._dimension}, entities={len(self._embeddings)})"


# Export
__all__ = [
    "SemanticIndex",
]
