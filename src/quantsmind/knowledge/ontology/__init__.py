"""
Ontology Package

This package provides ontology management for the Knowledge package.

Purpose
-------
Provide comprehensive ontology definitions and semantic understanding.

Modules
-------
- ontology: Base ontology class
- concept: Concept management
- category: Category management
- taxonomy: Taxonomy management
- vocabulary: Vocabulary management
- semantic_relation: Semantic relation management
"""

from __future__ import annotations

from quantsmind.knowledge.ontology.category import Category, CategoryHierarchy
from quantsmind.knowledge.ontology.concept import Concept
from quantsmind.knowledge.ontology.ontology import Ontology
from quantsmind.knowledge.ontology.semantic_relation import RelationRegistry, SemanticRelation
from quantsmind.knowledge.ontology.taxonomy import Taxonomy
from quantsmind.knowledge.ontology.vocabulary import Vocabulary

__all__ = [
    "Ontology",
    "Concept",
    "Category",
    "CategoryHierarchy",
    "Taxonomy",
    "Vocabulary",
    "SemanticRelation",
    "RelationRegistry",
]
