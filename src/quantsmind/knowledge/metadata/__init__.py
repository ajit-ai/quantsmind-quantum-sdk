"""
Metadata Package

This package provides metadata management for the Knowledge package.

Purpose
-------
Provide comprehensive metadata definitions and operations.

Modules
-------
- metadata: Base metadata class
- annotation: Annotation management
- tag: Tag management
- label: Label management
- property: Property management
- attribute: Attribute management
"""

from __future__ import annotations

from quantsmind.knowledge.metadata.annotation import Annotation
from quantsmind.knowledge.metadata.attribute import Attribute, AttributeSet
from quantsmind.knowledge.metadata.label import Label, LabelSet
from quantsmind.knowledge.metadata.metadata import KnowledgeMetadata
from quantsmind.knowledge.metadata.property import Property, PropertySet
from quantsmind.knowledge.metadata.tag import Tag, TagSet

__all__ = [
    "KnowledgeMetadata",
    "Annotation",
    "Tag",
    "TagSet",
    "Label",
    "LabelSet",
    "Property",
    "PropertySet",
    "Attribute",
    "AttributeSet",
]
