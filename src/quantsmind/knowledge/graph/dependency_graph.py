"""
Dependency Graph Module

This module provides dependency graph definitions for the Knowledge package.

Purpose
-------
Provide dependency graph management for representing dependencies between items.

Responsibilities
----------------
- Define dependency graph structure
- Support dependency operations
- Support dependency resolution
- Support cycle detection

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.graph.knowledge_graph (knowledge_graph)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from quantsmind.knowledge.enums import GraphType
from quantsmind.knowledge.exceptions import GraphError
from quantsmind.knowledge.graph.knowledge_graph import KnowledgeGraph
from quantsmind.knowledge.types import (
    EdgeData,
    GraphID,
    NodeData,
    ValidationResult,
)


class DependencyGraph(KnowledgeGraph):
    """Concrete implementation of a dependency graph.

    This class provides dependency graph functionality for representing dependencies between items.

    Attributes:
        _dependency_types: Dependency type definitions
        _directed: Whether dependencies are directed

    Example:
        >>> graph = DependencyGraph("dep_graph_001")
        >>> graph.add_dependency("item_001", "item_002", "requires")
    """

    def __init__(
        self,
        graph_id: GraphID,
        directed: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a DependencyGraph.

        Args:
            graph_id: Graph ID
            directed: Whether dependencies are directed
            metadata: Graph metadata

        Example:
            >>> graph = DependencyGraph("dep_graph_001")
        """
        super().__init__(graph_id, GraphType.DEPENDENCY, metadata)
        self._dependency_types: Dict[str, Dict[str, Any]] = {}
        self._directed = directed

    @property
    def dependency_types(self) -> Dict[str, Dict[str, Any]]:
        """Get the dependency types.

        Returns:
            Dependency type definitions

        Example:
            >>> dep_types = graph.dependency_types
        """
        return self._dependency_types.copy()

    @property
    def directed(self) -> bool:
        """Get whether dependencies are directed.

        Returns:
            True if directed

        Example:
            >>> directed = graph.directed
        """
        return self._directed

    def add_dependency_type(self, dep_type: str, description: Optional[str] = None, transitive: bool = False) -> None:
        """Add a dependency type definition.

        Args:
            dep_type: Dependency type
            description: Type description
            transitive: Whether the dependency is transitive

        Example:
            >>> graph.add_dependency_type("requires", "Required dependency", True)
        """
        self._dependency_types[dep_type] = {
            "description": description,
            "transitive": transitive,
        }

    def add_dependency(self, source: str, target: str, dep_type: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add a dependency to the graph.

        Args:
            source: Source item ID (dependent)
            target: Target item ID (dependency)
            dep_type: Dependency type
            attributes: Dependency attributes

        Example:
            >>> graph.add_dependency("item_001", "item_002", "requires")
        """
        if source not in self._nodes:
            raise GraphError("Source item not found", {"source": source})

        if target not in self._nodes:
            raise GraphError("Target item not found", {"target": target})

        edge_data = {"dependency_type": dep_type, **(attributes or {})}
        self.add_edge(source, target, edge_data)

    def remove_dependency(self, source: str, target: str, dep_type: Optional[str] = None) -> bool:
        """Remove a dependency from the graph.

        Args:
            source: Source item ID
            target: Target item ID
            dep_type: Dependency type (optional)

        Returns:
            True if removed

        Example:
            >>> removed = graph.remove_dependency("item_001", "item_002")
        """
        removed = False

        if dep_type:
            edge_data = self.get_edge(source, target)
            if edge_data and edge_data.get("dependency_type") == dep_type:
                removed = self.remove_edge(source, target)
        else:
            removed = self.remove_edge(source, target)

        return removed

    def get_dependencies(self, item_id: str, dep_type: Optional[str] = None) -> List[tuple[str, str, Dict[str, Any]]]:
        """Get dependencies for an item.

        Args:
            item_id: Item ID
            dep_type: Dependency type filter

        Returns:
            List of (target, dependency_type, attributes) tuples

        Example:
            >>> dependencies = graph.get_dependencies("item_001")
        """
        dependencies = []
        for neighbor in self.neighbors(item_id):
            edge_data = self.get_edge(item_id, neighbor)
            if edge_data:
                current_dep_type = edge_data.get("dependency_type")
                if dep_type is None or current_dep_type == dep_type:
                    dependencies.append((neighbor, current_dep_type, edge_data))
        return dependencies

    def get_dependents(self, item_id: str, dep_type: Optional[str] = None) -> List[str]:
        """Get items that depend on this item.

        Args:
            item_id: Item ID
            dep_type: Dependency type filter

        Returns:
            List of dependent item IDs

        Example:
            >>> dependents = graph.get_dependents("item_002")
        """
        dependents = []
        for (source, target), edge_data in self._edges.items():
            if target == item_id:
                current_dep_type = edge_data.get("dependency_type")
                if dep_type is None or current_dep_type == dep_type:
                    dependents.append(source)
        return dependents

    def get_all_dependencies(self, item_id: str, dep_type: Optional[str] = None) -> Set[str]:
        """Get all transitive dependencies for an item.

        Args:
            item_id: Item ID
            dep_type: Dependency type filter

        Returns:
            Set of all dependency IDs

        Example:
            >>> all_deps = graph.get_all_dependencies("item_001")
        """
        all_deps = set()
        visited = set()
        queue = [item_id]

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            for neighbor in self.neighbors(current):
                edge_data = self.get_edge(current, neighbor)
                if edge_data:
                    current_dep_type = edge_data.get("dependency_type")
                    if dep_type is None or current_dep_type == dep_type:
                        if neighbor not in all_deps:
                            all_deps.add(neighbor)
                            queue.append(neighbor)

        return all_deps

    def get_all_dependents(self, item_id: str, dep_type: Optional[str] = None) -> Set[str]:
        """Get all transitive dependents for an item.

        Args:
            item_id: Item ID
            dep_type: Dependency type filter

        Returns:
            Set of all dependent IDs

        Example:
            >>> all_dependents = graph.get_all_dependents("item_002")
        """
        all_dependents = set()
        visited = set()
        queue = [item_id]

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            for (source, target), edge_data in self._edges.items():
                if target == current:
                    current_dep_type = edge_data.get("dependency_type")
                    if dep_type is None or current_dep_type == dep_type:
                        if source not in all_dependents:
                            all_dependents.add(source)
                            queue.append(source)

        return all_dependents

    def detect_cycles(self) -> List[List[str]]:
        """Detect cycles in the dependency graph.

        Returns:
            List of cycles (each cycle is a list of node IDs)

        Example:
            >>> cycles = graph.detect_cycles()
        """
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.neighbors(node):
                if neighbor not in visited:
                    if dfs(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for node in self._nodes:
            if node not in visited:
                if dfs(node, []):
                    pass

        return cycles

    def topological_sort(self) -> Optional[List[str]]:
        """Perform topological sort of the graph.

        Returns:
            Sorted list of node IDs or None if cycle detected

        Example:
            >>> sorted_nodes = graph.topological_sort()
        """
        if self.detect_cycles():
            return None

        in_degree = {node: 0 for node in self._nodes}
        for (source, target) in self._edges.keys():
            in_degree[target] += 1

        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for neighbor in self.neighbors(node):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(self._nodes):
            return None

        return result

    def resolve_dependencies(self, item_id: str) -> List[str]:
        """Get dependency resolution order for an item.

        Args:
            item_id: Item ID

        Returns:
            List of item IDs in resolution order

        Example:
            >>> resolution_order = graph.resolve_dependencies("item_001")
        """
        all_deps = self.get_all_dependencies(item_id)
        subgraph_nodes = {item_id} | all_deps

        # Create subgraph for topological sort
        sorted_nodes = self.topological_sort()
        if sorted_nodes:
            return [node for node in sorted_nodes if node in subgraph_nodes]

        return []

    def validate(self) -> ValidationResult:
        """Validate the dependency graph.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = graph.validate()
        """
        errors = []

        # Validate base graph
        base_valid, base_errors = super().validate()
        errors.extend(base_errors)

        # Validate dependency types
        for (source, target), edge_data in self._edges.items():
            dep_type = edge_data.get("dependency_type")
            if dep_type and dep_type not in self._dependency_types:
                errors.append(f"Unknown dependency type: {dep_type}")

        # Check for cycles
        cycles = self.detect_cycles()
        if cycles:
            errors.append(f"Dependency graph contains {len(cycles)} cycle(s)")

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
            "dependency_types": self._dependency_types,
            "directed": self._directed,
            "has_cycles": len(self.detect_cycles()) > 0,
        })
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(graph)
        """
        return f"DependencyGraph(id={self._id}, dependencies={len(self._edges)}, directed={self._directed})"


# Export
__all__ = [
    "DependencyGraph",
]
