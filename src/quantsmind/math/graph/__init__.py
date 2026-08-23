"""
Graph Theory Module

This module provides graph theory operations for the Mathematics package.
Graph represents nodes, edges, and graph structures.

Purpose
-------
Provide graph theory operations for the Mathematics package.

Scientific Meaning
------------------
Graph theory represents the study of graphs (networks of connected nodes),
essential for network analysis, computer science, operations research, and many other scientific applications.

Responsibilities
----------------
- Support graph creation
- Enable graph traversal
- Support graph algorithms
- Handle graph validation

Dependencies
------------
typing (standard library)
quantsmind.math.exceptions (exception hierarchy)
quantsmind.math.types (type definitions)

Future Extensions
-----------------
- Graph algorithms (shortest path, MST, etc.)
- Graph visualization
- Network analysis
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from quantsmind.math.exceptions import GraphError
from quantsmind.math.types import Edge, Node

logger = logging.getLogger(__name__)


class Node:
    """Concrete implementation of a graph node.

    This class represents a node in a graph.

    Scientific Meaning
    ------------------
    In graph theory, a node (vertex) represents a fundamental unit of a graph,
    which can represent entities such as cities, people, atoms, or any other discrete objects.

    Attributes:
        _id: Node identifier
        _data: Optional node data

    Example:
        >>> node = Node("A", data={"label": "City A"})
    """

    def __init__(self, node_id: Any, data: dict[str, Any] | None = None) -> None:
        """Initialize a Node.

        Args:
            node_id: Node identifier
            data: Optional node data

        Example:
            >>> node = Node("A", data={"label": "City A"})
        """
        self._id = node_id
        self._data = data or {}
        logger.debug(f"Created node: {node_id}")

    @property
    def id(self) -> Any:
        """Get the node ID.

        Returns:
            Node identifier

        Example:
            >>> print(f"ID: {node.id}")
        """
        return self._id

    @property
    def data(self) -> dict[str, Any]:
        """Get the node data.

        Returns:
            Node data

        Example:
            >>> print(f"Data: {node.data}")
        """
        return self._data.copy()

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(node)
        """
        return f"Node({self._id})"

    def __str__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> str(node)
        """
        return str(self._id)

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> node1 == node2
        """
        if not isinstance(other, Node):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Return hash.

        Returns:
            Hash value

        Example:
            >>> hash(node)
        """
        return hash(self._id)


class Edge:
    """Concrete implementation of a graph edge.

    This class represents an edge in a graph.

    Scientific Meaning
    ------------------
    In graph theory, an edge represents a connection between two nodes,
    which can represent relationships, paths, or interactions.

    Attributes:
        _source: Source node
        _target: Target node
        _weight: Optional edge weight
        _data: Optional edge data

    Example:
        >>> edge = Edge(Node("A"), Node("B"), weight=5.0)
    """

    def __init__(
        self,
        source: Node,
        target: Node,
        weight: float | None = None,
        data: dict[str, Any] | None = None
    ) -> None:
        """Initialize an Edge.

        Args:
            source: Source node
            target: Target node
            weight: Optional edge weight
            data: Optional edge data

        Example:
            >>> edge = Edge(Node("A"), Node("B"), weight=5.0)
        """
        self._source = source
        self._target = target
        self._weight = weight
        self._data = data or {}
        logger.debug(f"Created edge: {source.id} -> {target.id}")

    @property
    def source(self) -> Node:
        """Get the source node.

        Returns:
            Source node

        Example:
            >>> print(f"Source: {edge.source}")
        """
        return self._source

    @property
    def target(self) -> Node:
        """Get the target node.

        Returns:
            Target node

        Example:
            >>> print(f"Target: {edge.target}")
        """
        return self._target

    @property
    def weight(self) -> float | None:
        """Get the edge weight.

        Returns:
            Edge weight or None

        Example:
            >>> print(f"Weight: {edge.weight}")
        """
        return self._weight

    @property
    def data(self) -> dict[str, Any]:
        """Get the edge data.

        Returns:
            Edge data

        Example:
            >>> print(f"Data: {edge.data}")
        """
        return self._data.copy()

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(edge)
        """
        weight_str = f", weight={self._weight}" if self._weight is not None else ""
        return f"Edge({self._source.id} -> {self._target.id}{weight_str})"

    def __str__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> str(edge)
        """
        return f"{self._source.id} -> {self._target.id}"

    def __eq__(self, other: Any) -> bool:
        """Check equality.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise

        Example:
            >>> edge1 == edge2
        """
        if not isinstance(other, Edge):
            return False
        return self._source == other._source and self._target == other._target

    def __hash__(self) -> int:
        """Return hash.

        Returns:
            Hash value

        Example:
            >>> hash(edge)
        """
        return hash((self._source, self._target))


class Graph:
    """Concrete implementation of a graph.

    This class represents a graph with nodes and edges.

    Scientific Meaning
    ------------------
    In graph theory, a graph represents a collection of nodes connected by edges,
    used to model relationships, networks, and structures.

    Attributes:
        _nodes: Dictionary of nodes
        _edges: List of edges
        _directed: Whether the graph is directed

    Example:
        >>> graph = Graph(directed=False)
        >>> graph.add_node(Node("A"))
        >>> graph.add_node(Node("B"))
        >>> graph.add_edge(Edge(Node("A"), Node("B")))
    """

    def __init__(self, directed: bool = False) -> None:
        """Initialize a Graph.

        Args:
            directed: Whether the graph is directed

        Example:
            >>> graph = Graph(directed=False)
        """
        self._nodes: dict[Any, Node] = {}
        self._edges: list[Edge] = []
        self._directed = directed
        logger.debug(f"Created {'directed' if directed else 'undirected'} graph")

    @property
    def directed(self) -> bool:
        """Get whether the graph is directed.

        Returns:
            True if directed, False otherwise

        Example:
            >>> print(f"Directed: {graph.directed}")
        """
        return self._directed

    @property
    def node_count(self) -> int:
        """Get the number of nodes.

        Returns:
            Number of nodes

        Example:
            >>> print(f"Node count: {graph.node_count}")
        """
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        """Get the number of edges.

        Returns:
            Number of edges

        Example:
            >>> print(f"Edge count: {graph.edge_count}")
        """
        return len(self._edges)

    def add_node(self, node: Node) -> None:
        """Add a node to the graph.

        Args:
            node: Node to add

        Example:
            >>> graph.add_node(Node("A"))
        """
        self._nodes[node.id] = node
        logger.debug(f"Added node: {node.id}")

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph.

        Args:
            edge: Edge to add

        Raises:
            GraphError: If nodes don't exist

        Example:
            >>> graph.add_edge(Edge(Node("A"), Node("B")))
        """
        if edge.source.id not in self._nodes:
            raise GraphError(f"Source node {edge.source.id} not found in graph")
        if edge.target.id not in self._nodes:
            raise GraphError(f"Target node {edge.target.id} not found in graph")
        self._edges.append(edge)
        logger.debug(f"Added edge: {edge.source.id} -> {edge.target.id}")

    def get_node(self, node_id: Any) -> Node | None:
        """Get a node by ID.

        Args:
            node_id: Node ID

        Returns:
            Node or None

        Example:
            >>> node = graph.get_node("A")
        """
        return self._nodes.get(node_id)

    def get_neighbors(self, node_id: Any) -> list[Node]:
        """Get neighbors of a node.

        Args:
            node_id: Node ID

        Returns:
            List of neighbor nodes

        Raises:
            GraphError: If node doesn't exist

        Example:
            >>> neighbors = graph.get_neighbors("A")
        """
        if node_id not in self._nodes:
            raise GraphError(f"Node {node_id} not found in graph")
        
        neighbors = []
        for edge in self._edges:
            if edge.source.id == node_id:
                neighbors.append(edge.target)
            if not self._directed and edge.target.id == node_id:
                neighbors.append(edge.source)
        return neighbors

    def has_edge(self, source_id: Any, target_id: Any) -> bool:
        """Check if an edge exists.

        Args:
            source_id: Source node ID
            target_id: Target node ID

        Returns:
            True if edge exists, False otherwise

        Example:
            >>> if graph.has_edge("A", "B"):
            ...     print("Edge exists")
        """
        for edge in self._edges:
            if edge.source.id == source_id and edge.target.id == target_id:
                return True
            if not self._directed and edge.source.id == target_id and edge.target.id == source_id:
                return True
        return False

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(graph)
        """
        return f"Graph(nodes={self.node_count}, edges={self.edge_count}, directed={self._directed})"


class DirectedGraph(Graph):
    """Concrete implementation of a directed graph.

    This class represents a directed graph where edges have direction.

    Example:
        >>> graph = DirectedGraph()
        >>> graph.add_node(Node("A"))
        >>> graph.add_node(Node("B"))
        >>> graph.add_edge(Edge(Node("A"), Node("B")))
    """

    def __init__(self) -> None:
        """Initialize a DirectedGraph.

        Example:
            >>> graph = DirectedGraph()
        """
        super().__init__(directed=True)


class WeightedGraph(Graph):
    """Concrete implementation of a weighted graph.

    This class represents a weighted graph where edges have weights.

    Example:
        >>> graph = WeightedGraph()
        >>> graph.add_node(Node("A"))
        >>> graph.add_node(Node("B"))
        >>> graph.add_edge(Edge(Node("A"), Node("B"), weight=5.0))
    """

    def __init__(self, directed: bool = False) -> None:
        """Initialize a WeightedGraph.

        Args:
            directed: Whether the graph is directed

        Example:
            >>> graph = WeightedGraph(directed=False)
        """
        super().__init__(directed=directed)

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the weighted graph.

        Args:
            edge: Edge to add

        Raises:
            GraphError: If edge has no weight

        Example:
            >>> graph.add_edge(Edge(Node("A"), Node("B"), weight=5.0))
        """
        if edge.weight is None:
            raise GraphError("Weighted graph requires edges with weights")
        super().add_edge(edge)

    def get_edge_weight(self, source_id: Any, target_id: Any) -> float | None:
        """Get the weight of an edge.

        Args:
            source_id: Source node ID
            target_id: Target node ID

        Returns:
            Edge weight or None

        Example:
            >>> weight = graph.get_edge_weight("A", "B")
        """
        for edge in self._edges:
            if edge.source.id == source_id and edge.target.id == target_id:
                return edge.weight
            if not self._directed and edge.source.id == target_id and edge.target.id == source_id:
                return edge.weight
        return None


# Export
__all__ = [
    "Node",
    "Edge",
    "Graph",
    "DirectedGraph",
    "WeightedGraph",
]
