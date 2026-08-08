"""
Knowledge Types Module

This module provides type definitions for the Knowledge package.

Purpose
-------
Define type aliases and type hints for knowledge management.

Responsibilities
----------------
- Define dataset type aliases
- Define metadata type aliases
- Define ontology type aliases
- Define graph type aliases
- Define provenance type aliases
- Define reasoning type aliases
- Define quality type aliases
- Define search type aliases
- Define transformation type aliases
- Define evidence type aliases

Dependencies
------------
typing (standard library)
datetime (standard library)
uuid (standard library)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from uuid import UUID

# Dataset types
DatasetID = Union[str, UUID]
DatasetName = str
DatasetVersion = str
DatasetSize = int
RecordCount = int
DatasetData = Union[List[Dict[str, Any]], Dict[str, Any]]
DatasetSchema = Dict[str, Any]

# Metadata types
MetadataID = Union[str, UUID]
MetadataKey = str
MetadataValue = Any
MetadataDict = Dict[MetadataKey, MetadataValue]
Tag = str
Label = str
Annotation = str
Property = str
Attribute = str

# Ontology types
OntologyID = Union[str, UUID]
ConceptID = Union[str, UUID]
ConceptName = str
CategoryID = Union[str, UUID]
TaxonomyID = Union[str, UUID]
VocabularyID = Union[str, UUID]
RelationID = Union[str, UUID]
RelationType = str

# Graph types
GraphID = Union[str, UUID]
NodeID = Union[str, UUID]
EdgeID = Union[str, UUID]
NodeData = Dict[str, Any]
EdgeData = Dict[str, Any]
AdjacencyList = Dict[NodeID, List[Tuple[NodeID, EdgeData]]]
Path = List[NodeID]

# Provenance types
ProvenanceID = Union[str, UUID]
SourceID = Union[str, UUID]
CreatorID = Union[str, UUID]
ExperimentID = Union[str, UUID]
WorkflowID = Union[str, UUID]
HistoryID = Union[str, UUID]
AuditID = Union[str, UUID]
ProvenanceChain = List[Dict[str, Any]]

# Lineage types
LineageID = Union[str, UUID]
LineageNodeID = Union[str, UUID]
LineageEdgeID = Union[str, UUID]
LineageGraph = Dict[LineageNodeID, List[LineageNodeID]]

# Observation types
ObservationID = Union[str, UUID]
ObservationSessionID = Union[str, UUID]
ObservationData = Dict[str, Any]
ObservationTimestamp = datetime

# Measurement types
MeasurementID = Union[str, UUID]
MeasurementValue = Union[int, float]
MeasurementUnit = str
MeasurementData = Dict[str, Any]

# Quality types
QualityRuleID = Union[str, UUID]
QualityScore = float
QualityReport = Dict[str, Any]

# Transformation types
TransformationID = Union[str, UUID]
PipelineID = Union[str, UUID]
MappingFunction = Callable[[Any], Any]
ConverterFunction = Callable[[Any], Any]

# Indexing types
IndexID = Union[str, UUID]
IndexKey = Union[str, Tuple[str, ...]]
IndexValue = Any
IndexData = Dict[IndexKey, IndexValue]

# Search types
SearchQuery = str
SearchResults = List[Dict[str, Any]]
SearchScore = float
SearchFilter = Dict[str, Any]

# Repository types
RepositoryID = Union[str, UUID]
KnowledgeItemID = Union[str, UUID]
KnowledgeItemData = Dict[str, Any]

# Reasoning types
ReasoningID = Union[str, UUID]
InferenceID = Union[str, UUID]
RuleID = Union[str, UUID]
Explanation = str
Prediction = Dict[str, Any]
Confidence = float

# Evidence types
EvidenceID = Union[str, UUID]
HypothesisID = Union[str, UUID]
TheoryID = Union[str, UUID]
LawID = Union[str, UUID]
FactID = Union[str, UUID]
EvidenceChain = List[EvidenceID]

# Validation types
ValidationResult = Tuple[bool, List[str]]
ValidationRule = Callable[[Any], ValidationResult]
ValidationReport = Dict[str, Any]

# Serialization types
SerializedData = Union[str, bytes, Dict[str, Any]]
SerializationOptions = Dict[str, Any]

# Versioning types
Version = str
VersionID = Union[str, UUID]
VersionMetadata = Dict[str, Any]

# Data source types
DataSourceID = Union[str, UUID]
DataSourceConfig = Dict[str, Any]
DataSourceConnection = Any

# General knowledge types
KnowledgeID = Union[str, UUID]
KnowledgeData = Dict[str, Any]
KnowledgeGraph = Dict[NodeID, List[Tuple[NodeID, EdgeData]]]
KnowledgeMetadata = MetadataDict

# Lifecycle types
LifecycleStage = str
LifecycleState = str
LifecycleTransition = Tuple[LifecycleStage, LifecycleStage]

# Entity types
EntityID = Union[str, UUID]
EntityType = str
EntityData = Dict[str, Any]
EntityState = str

# State types
StateID = Union[str, UUID]
StateData = Dict[str, Any]
StateTransition = Tuple[StateID, StateID]

# Interaction types
InteractionID = Union[str, UUID]
InteractionType = str
InteractionData = Dict[str, Any]

# Data types
DataID = Union[str, UUID]
DataType = str
DataValue = Any

# Information types
InformationID = Union[str, UUID]
InformationData = Dict[str, Any]

# Knowledge types
KnowledgeType = str
KnowledgeContent = Any

# Decision types
DecisionID = Union[str, UUID]
DecisionData = Dict[str, Any]
DecisionOutcome = str

# Action types
ActionID = Union[str, UUID]
ActionType = str
ActionData = Dict[str, Any]

# Evolution types
EvolutionID = Union[str, UUID]
EvolutionData = Dict[str, Any]

# Export
__all__ = [
    # Dataset types
    "DatasetID",
    "DatasetName",
    "DatasetVersion",
    "DatasetSize",
    "RecordCount",
    "DatasetData",
    "DatasetSchema",
    # Metadata types
    "MetadataID",
    "MetadataKey",
    "MetadataValue",
    "MetadataDict",
    "Tag",
    "Label",
    "Annotation",
    "Property",
    "Attribute",
    # Ontology types
    "OntologyID",
    "ConceptID",
    "ConceptName",
    "CategoryID",
    "TaxonomyID",
    "VocabularyID",
    "RelationID",
    "RelationType",
    # Graph types
    "GraphID",
    "NodeID",
    "EdgeID",
    "NodeData",
    "EdgeData",
    "AdjacencyList",
    "Path",
    # Provenance types
    "ProvenanceID",
    "SourceID",
    "CreatorID",
    "ExperimentID",
    "WorkflowID",
    "HistoryID",
    "AuditID",
    "ProvenanceChain",
    # Lineage types
    "LineageID",
    "LineageNodeID",
    "LineageEdgeID",
    "LineageGraph",
    # Observation types
    "ObservationID",
    "ObservationSessionID",
    "ObservationData",
    "ObservationTimestamp",
    # Measurement types
    "MeasurementID",
    "MeasurementValue",
    "MeasurementUnit",
    "MeasurementData",
    # Quality types
    "QualityRuleID",
    "QualityScore",
    "QualityReport",
    # Transformation types
    "TransformationID",
    "PipelineID",
    "MappingFunction",
    "ConverterFunction",
    # Indexing types
    "IndexID",
    "IndexKey",
    "IndexValue",
    "IndexData",
    # Search types
    "SearchQuery",
    "SearchResults",
    "SearchScore",
    "SearchFilter",
    # Repository types
    "RepositoryID",
    "KnowledgeItemID",
    "KnowledgeItemData",
    # Reasoning types
    "ReasoningID",
    "InferenceID",
    "RuleID",
    "Explanation",
    "Prediction",
    "Confidence",
    # Evidence types
    "EvidenceID",
    "HypothesisID",
    "TheoryID",
    "LawID",
    "FactID",
    "EvidenceChain",
    # Validation types
    "ValidationResult",
    "ValidationRule",
    "ValidationReport",
    # Serialization types
    "SerializedData",
    "SerializationOptions",
    # Versioning types
    "Version",
    "VersionID",
    "VersionMetadata",
    # Data source types
    "DataSourceID",
    "DataSourceConfig",
    "DataSourceConnection",
    # General knowledge types
    "KnowledgeID",
    "KnowledgeData",
    "KnowledgeGraph",
    "KnowledgeMetadata",
    # Lifecycle types
    "LifecycleStage",
    "LifecycleState",
    "LifecycleTransition",
    # Entity types
    "EntityID",
    "EntityType",
    "EntityData",
    "EntityState",
    # State types
    "StateID",
    "StateData",
    "StateTransition",
    # Interaction types
    "InteractionID",
    "InteractionType",
    "InteractionData",
    # Data types
    "DataID",
    "DataType",
    "DataValue",
    # Information types
    "InformationID",
    "InformationData",
    # Knowledge types
    "KnowledgeType",
    "KnowledgeContent",
    # Decision types
    "DecisionID",
    "DecisionData",
    "DecisionOutcome",
    # Action types
    "ActionID",
    "ActionType",
    "ActionData",
    # Evolution types
    "EvolutionID",
    "EvolutionData",
]
