"""
Graph Search Module

This module provides graph search definitions for the Knowledge package.

Purpose
-------
Provide graph search management for knowledge retrieval.

Responsibilities
----------------
- Define graph search structure
- Support graph search operations
- Support graph search validation
- Support graph search metadata

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


class GraphSearch(ISearchEngine):
    """Concrete implementation of a graph search engine.

    This class provides graph search functionality.

    Attributes:
        _id: Search engine ID
        _name: Search engine name
        _search_type: Search type
        _graph: Graph structure
        _metadata: Search engine metadata

    Example:
        >>> graph_search = GraphSearch("graph_search_001", "Graph Search")
        >>> graph_search.add_node("node_001", {"label": "Test"})
    """

    def __init__(
        self,
        search_id: str,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a GraphSearch.

        Args:
            search_id: Search engine ID
            name: Search engine name
            metadata: Search engine metadata

        Example:
            >>> graph_search = GraphSearch("graph_search_001", "Graph Search")
        """
        if not search_id:
            raise SearchError("Search ID cannot be empty", {"search_id": search_id})

        if not name:
            raise SearchError("Search name cannot be empty", {"name": name})

        self._id = search_id
        self._name = name
        self._search_type = SearchType.GRAPH
        self._graph: dict[str, dict[str, Any]] = {}
        self._edges: list[tuple[str, str]] = []
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Get the search engine ID.

        Returns:
            Search engine ID

        Example:
            >>> sid = graph_search.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the search engine name.

        Returns:
            Search engine name

        Example:
            >>> name = graph_search.name
        """
        return self._name

    @property
    def search_type(self) -> SearchType:
        """Get the search type.

        Returns:
            Search type

        Example:
            >>> stype = graph_search.search_type
        """
        return self._search_type

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the search engine metadata.

        Returns:
            Search engine metadata

        Example:
            >>> metadata = graph_search.metadata
        """
        return self._metadata.copy()

    def add_node(self, node_id: str, data: dict[str, Any]) -> None:
        """Add a node to the graph.

        Args:
            node_id: Node ID
            data: Node data

        Example:
            >>> graph_search.add_node("node_001", {"label": "Test"})
        """
        self._graph[node_id] = data

    def add_edge(self, source: str, target: str) -> None:
        """Add an edge to the graph.

        Args:
            source: Source node
            target: Target node

        Example:
            >>> graph_search.add_edge("node_001", "node_002")
        """
        self._edges.append((source, target))

    def index_document(self, doc_id: str, document: dict[str, Any]) -> None:
        """Index a document as a node.

        Args:
            doc_id: Document ID
            document: Document data

        Example:
            >>> graph_search.index_document("doc_001", {"label": "Test"})
        """
        self.add_node(doc_id, document)

    def remove_document(self, doc_id: str) -> bool:
        """Remove a document from the graph.

        Args:
            doc_id: Document ID

        Returns:
            True if removed

        Example:
            >>> removed = graph_search.remove_document("doc_001")
        """
        if doc_id in self._graph:
            del self._graph[doc_id]
            # Remove edges involving this node
            self._edges = [(s, t) for s, t in self._edges if s != doc_id and t != doc_id]
            return True
        return False

    def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        """Search for nodes matching the query.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of search results

        Example:
            >>> results = graph_search.search("Test")
        """
        results = []
        query_lower = query.lower()

        for node_id, data in self._graph.items():
            score = 0.0
            # Simple text matching
            for _field, value in data.items():
                if isinstance(value, str) and query_lower in value.lower():
                    score += 1.0

            if score > 0:
                results.append(SearchResult(node_id, score, data))

        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def search_neighbors(self, node_id: str, depth: int = 1) -> list[str]:
        """Search for neighbors of a node.

        Args:
            node_id: Node ID
            depth: Search depth

        Returns:
            List of neighbor node IDs

        Example:
            >>> neighbors = graph_search.search_neighbors("node_001", depth=2)
        """
        neighbors = set()
        visited = {node_id}
        queue = [(node_id, 0)]

        while queue:
            current, current_depth = queue.pop(0)

            if current_depth >= depth:
                continue

            for source, target in self._edges:
                if source == current and target not in visited:
                    visited.add(target)
                    neighbors.add(target)
                    queue.append((target, current_depth + 1))

        return list(neighbors)

    def search_path(self, source: str, target: str) -> list[str] | None:
        """Search for a path between two nodes.

        Args:
            source: Source node
            target: Target node

        Returns:
            Path or None

        Example:
            >>> path = graph_search.search_path("node_001", "node_003")
        """
        if source not in self._graph or target not in self._graph:
            return None

        if source == target:
            return [source]

        from collections import deque

        queue = deque([(source, [source])])
        visited = {source}

        while queue:
            current, path = queue.popleft()

            for s, t in self._edges:
                if s == current and t not in visited:
                    if t == target:
                        return path + [target]
                    visited.add(t)
                    queue.append((t, path + [t]))

        return None

    def validate(self) -> ValidationResult:
        """Validate the graph search.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = graph_search.validate()
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
            >>> data = graph_search.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "search_type": self._search_type.value,
            "node_count": len(self._graph),
            "edge_count": len(self._edges),
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(graph_search)
        """
        return f"GraphSearch(id={self._id}, name={self._name}, nodes={len(self._graph)}, edges={len(self._edges)})"


# Export
__all__ = [
    "GraphSearch",
]
