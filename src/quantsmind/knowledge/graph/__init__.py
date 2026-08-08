"""
Graph Package

This package provides graph management for the Knowledge package.

Purpose
-------
Provide comprehensive graph definitions and operations.

Modules
-------
- knowledge_graph: Base knowledge graph class
- entity_graph: Entity graph for representing entities
- relationship_graph: Relationship graph for representing relationships
- semantic_graph: Semantic graph for representing semantic relationships
- dependency_graph: Dependency graph for representing dependencies
"""

from __future__ import annotations

from quantsmind.knowledge.graph.dependency_graph import DependencyGraph
from quantsmind.knowledge.graph.entity_graph import EntityGraph
from quantsmind.knowledge.graph.knowledge_graph import KnowledgeGraph
from quantsmind.knowledge.graph.relationship_graph import RelationshipGraph
from quantsmind.knowledge.graph.semantic_graph import SemanticGraph

__all__ = [
    "KnowledgeGraph",
    "EntityGraph",
    "RelationshipGraph",
    "SemanticGraph",
    "DependencyGraph",
]
