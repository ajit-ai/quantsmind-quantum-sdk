"""
Semantic Graph Module

This module provides semantic graph definitions for the Knowledge package.

Purpose
-------
Provide semantic graph management for representing semantic relationships.

Responsibilities
----------------
- Define semantic graph structure
- Support semantic operations
- Support semantic similarity
- Support semantic validation

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.graph.knowledge_graph (knowledge_graph)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from quantsmind.knowledge.enums import GraphType
from quantsmind.knowledge.exceptions import GraphError
from quantsmind.knowledge.graph.knowledge_graph import KnowledgeGraph
from quantsmind.knowledge.types import (
    EdgeData,
    GraphID,
    NodeData,
    ValidationResult,
)


class SemanticGraph(KnowledgeGraph):
    """Concrete implementation of a semantic graph.

    This class provides semantic graph functionality for representing semantic relationships between concepts.

    Attributes:
        _semantic_types: Semantic type definitions
        _similarity_threshold: Similarity threshold for semantic matching

    Example:
        >>> graph = SemanticGraph("semantic_graph_001")
        >>> graph.add_semantic_link("concept_001", "concept_002", "synonym")
    """

    def __init__(
        self,
        graph_id: GraphID,
        similarity_threshold: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a SemanticGraph.

        Args:
            graph_id: Graph ID
            similarity_threshold: Threshold for semantic similarity
            metadata: Graph metadata

        Example:
            >>> graph = SemanticGraph("semantic_graph_001")
        """
        super().__init__(graph_id, GraphType.SEMANTIC, metadata)
        self._semantic_types: Dict[str, Dict[str, Any]] = {}
        self._similarity_threshold = similarity_threshold

    @property
    def semantic_types(self) -> Dict[str, Dict[str, Any]]:
        """Get the semantic types.

        Returns:
            Semantic type definitions

        Example:
            >>> sem_types = graph.semantic_types
        """
        return self._semantic_types.copy()

    @property
    def similarity_threshold(self) -> float:
        """Get the similarity threshold.

        Returns:
            Similarity threshold

        Example:
            >>> threshold = graph.similarity_threshold
        """
        return self._similarity_threshold

    def add_semantic_type(self, sem_type: str, description: Optional[str] = None, weight: float = 1.0) -> None:
        """Add a semantic type definition.

        Args:
            sem_type: Semantic type
            description: Type description
            weight: Type weight for similarity calculation

        Example:
            >>> graph.add_semantic_type("synonym", "Synonym relationship", 1.0)
        """
        self._semantic_types[sem_type] = {
            "description": description,
            "weight": weight,
        }

    def add_semantic_link(self, source: str, target: str, sem_type: str, similarity: float = 1.0, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add a semantic link to the graph.

        Args:
            source: Source concept ID
            target: Target concept ID
            sem_type: Semantic type
            similarity: Similarity score (0.0 to 1.0)
            attributes: Link attributes

        Example:
            >>> graph.add_semantic_link("concept_001", "concept_002", "synonym")
        """
        if source not in self._nodes:
            raise GraphError("Source concept not found", {"source": source})

        if target not in self._nodes:
            raise GraphError("Target concept not found", {"target": target})

        if similarity < 0.0 or similarity > 1.0:
            raise GraphError("Similarity must be between 0.0 and 1.0", {"similarity": similarity})

        edge_data = {
            "semantic_type": sem_type,
            "similarity": similarity,
            **(attributes or {})
        }
        self.add_edge(source, target, edge_data)

    def remove_semantic_link(self, source: str, target: str, sem_type: Optional[str] = None) -> bool:
        """Remove a semantic link from the graph.

        Args:
            source: Source concept ID
            target: Target concept ID
            sem_type: Semantic type (optional)

        Returns:
            True if removed

        Example:
            >>> removed = graph.remove_semantic_link("concept_001", "concept_002")
        """
        removed = False

        if sem_type:
            edge_data = self.get_edge(source, target)
            if edge_data and edge_data.get("semantic_type") == sem_type:
                removed = self.remove_edge(source, target)
        else:
            removed = self.remove_edge(source, target)

        return removed

    def get_semantic_links(self, concept_id: str, sem_type: Optional[str] = None, min_similarity: Optional[float] = None) -> List[tuple[str, str, float]]:
        """Get semantic links for a concept.

        Args:
            concept_id: Concept ID
            sem_type: Semantic type filter
            min_similarity: Minimum similarity filter

        Returns:
            List of (target, semantic_type, similarity) tuples

        Example:
            >>> links = graph.get_semantic_links("concept_001")
        """
        links = []
        for neighbor in self.neighbors(concept_id):
            edge_data = self.get_edge(concept_id, neighbor)
            if edge_data:
                current_sem_type = edge_data.get("semantic_type")
                similarity = edge_data.get("similarity", 1.0)

                if sem_type is None or current_sem_type == sem_type:
                    if min_similarity is None or similarity >= min_similarity:
                        links.append((neighbor, current_sem_type, similarity))
        return links

    def get_similar_concepts(self, concept_id: str, min_similarity: Optional[float] = None) -> List[tuple[str, float]]:
        """Get similar concepts.

        Args:
            concept_id: Concept ID
            min_similarity: Minimum similarity (uses threshold if not specified)

        Returns:
            List of (concept_id, similarity) tuples

        Example:
            >>> similar = graph.get_similar_concepts("concept_001")
        """
        if min_similarity is None:
            min_similarity = self._similarity_threshold

        similar = []
        for neighbor in self.neighbors(concept_id):
            edge_data = self.get_edge(concept_id, neighbor)
            if edge_data:
                similarity = edge_data.get("similarity", 1.0)
                if similarity >= min_similarity:
                    similar.append((neighbor, similarity))

        # Sort by similarity descending
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar

    def calculate_semantic_similarity(self, concept1: str, concept2: str) -> Optional[float]:
        """Calculate semantic similarity between two concepts.

        Args:
            concept1: First concept ID
            concept2: Second concept ID

        Returns:
            Similarity score or None

        Example:
            >>> similarity = graph.calculate_semantic_similarity("concept_001", "concept_002")
        """
        edge_data = self.get_edge(concept1, concept2)
        if edge_data:
            return edge_data.get("similarity", 1.0)

        # Check reverse direction
        edge_data = self.get_edge(concept2, concept1)
        if edge_data:
            return edge_data.get("similarity", 1.0)

        return None

    def find_shortest_semantic_path(self, source: str, target: str) -> Optional[List[str]]:
        """Find shortest semantic path between concepts.

        Args:
            source: Source concept ID
            target: Target concept ID

        Returns:
            Path or None

        Example:
            >>> path = graph.find_shortest_semantic_path("concept_001", "concept_002")
        """
        return self.shortest_path(source, target)

    def get_semantic_neighbors(self, concept_id: str, radius: int = 1) -> Dict[str, List[str]]:
        """Get semantic neighbors within a radius.

        Args:
            concept_id: Concept ID
            radius: Search radius

        Returns:
            Dictionary of {distance: [concept_ids]}

        Example:
            >>> neighbors = graph.get_semantic_neighbors("concept_001", radius=2)
        """
        neighbors = {i: [] for i in range(1, radius + 1)}

        visited = {concept_id}
        current_level = [concept_id]

        for distance in range(1, radius + 1):
            next_level = []
            for node in current_level:
                for neighbor in self.neighbors(node):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_level.append(neighbor)
                        neighbors[distance].append(neighbor)

            current_level = next_level

        return neighbors

    def validate(self) -> ValidationResult:
        """Validate the semantic graph.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = graph.validate()
        """
        errors = []

        # Validate base graph
        base_valid, base_errors = super().validate()
        errors.extend(base_errors)

        # Validate semantic types
        for (source, target), edge_data in self._edges.items():
            sem_type = edge_data.get("semantic_type")
            if sem_type and sem_type not in self._semantic_types:
                errors.append(f"Unknown semantic type: {sem_type}")

        # Validate similarity scores
        for (source, target), edge_data in self._edges.items():
            similarity = edge_data.get("similarity")
            if similarity is not None and (similarity < 0.0 or similarity > 1.0):
                errors.append(f"Invalid similarity score in edge ({source}, {target})")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Graph definition

        Example:
            >>> data = graph.to_dict()
        """
        data = super().to_dict()
        data.update({
            "semantic_types": self._semantic_types,
            "similarity_threshold": self._similarity_threshold,
        })
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(graph)
        """
        return f"SemanticGraph(id={self._id}, semantic_links={len(self._edges)}, threshold={self._similarity_threshold})"


# Export
__all__ = [
    "SemanticGraph",
]
