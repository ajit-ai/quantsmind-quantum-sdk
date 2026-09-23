"""
Knowledge Package

This package provides the Knowledge & Reasoning Framework for the QuantsMind SDK.

Purpose
-------
Provide comprehensive knowledge management and reasoning capabilities for the SDK.

Version
-------
R0.7.0

Modules
-------
- foundational: Foundational modules (exceptions, enums, types, interfaces, protocols, constants, factories)
- dataset: Dataset management
- datasource: Datasource management
- metadata: Metadata management
- schema: Schema management
- ontology: Ontology management
- graph: Graph management
- provenance: Provenance management
- lineage: Lineage management
- observation: Observation management
- measurement: Measurement management
- quality: Quality management
- transformation: Transformation management
- indexing: Indexing management
- search: Search management
- repository: Repository management
- reasoning: Reasoning management
- evidence: Evidence management
- validation: Validation management
- serialization: Serialization management
- versioning: Versioning management
"""

from __future__ import annotations

# Dataset modules
from quantsmind.knowledge.dataset.dataset import Dataset
from quantsmind.knowledge.dataset.dataset_registry import DatasetRegistry
from quantsmind.knowledge.dataset.graph_dataset import GraphDataset
from quantsmind.knowledge.dataset.image_dataset import ImageDataset
from quantsmind.knowledge.dataset.quantum_dataset import QuantumDataset
from quantsmind.knowledge.dataset.scientific_dataset import ScientificDataset
from quantsmind.knowledge.dataset.simulation_dataset import SimulationDataset
from quantsmind.knowledge.dataset.tensor_dataset import TensorDataset
from quantsmind.knowledge.datasource.api_source import APISource
from quantsmind.knowledge.datasource.database_source import DatabaseSource

# Datasource modules
from quantsmind.knowledge.datasource.datasource import DataSource
from quantsmind.knowledge.datasource.file_source import FileSource
from quantsmind.knowledge.datasource.stream_source import StreamSource

# Evidence modules
from quantsmind.knowledge.evidence.evidence import Evidence
from quantsmind.knowledge.evidence.fact import Fact
from quantsmind.knowledge.evidence.hypothesis import Hypothesis
from quantsmind.knowledge.evidence.law import Law
from quantsmind.knowledge.evidence.rule import Rule as EvidenceRule
from quantsmind.knowledge.evidence.theory import Theory

# Foundational modules
from quantsmind.knowledge.constants import (
    DEFAULT_TIMEOUT,
    MAX_BATCH_SIZE,
    SDK_VERSION,
)
from quantsmind.knowledge.enums import (
    DataType,
    EvidenceType,
    IndexType,
    OntologyType,
    ProvenanceType,
    QualityType,
    ReasoningType,
    RepositoryType,
    SchemaType,
    SearchType,
    SerializationType,
    TransformationType,
    ValidationType,
    VersionType,
)
from quantsmind.knowledge.exceptions import (
    DatasetError,
    DatasourceError,
    EvidenceError,
    GraphError,
    IndexError,
    KnowledgeError,
    LineageError,
    MeasurementError,
    ObservationError,
    OntologyError,
    ProvenanceError,
    QualityError,
    ReasoningError,
    RepositoryError,
    SchemaError,
    SearchError,
    SerializationError,
    TransformationError,
    ValidationError,
    VersionError,
)
from quantsmind.knowledge.graph.dependency_graph import DependencyGraph
from quantsmind.knowledge.graph.entity_graph import EntityGraph

# Graph modules
from quantsmind.knowledge.graph.knowledge_graph import KnowledgeGraph
from quantsmind.knowledge.graph.relationship_graph import RelationshipGraph
from quantsmind.knowledge.graph.semantic_graph import SemanticGraph
from quantsmind.knowledge.indexing.graph_index import GraphIndex

# Indexing modules
from quantsmind.knowledge.indexing.index import Index
from quantsmind.knowledge.indexing.semantic_index import SemanticIndex

# Lineage modules
from quantsmind.knowledge.lineage.lineage import Lineage
from quantsmind.knowledge.lineage.lineage_edge import LineageEdge
from quantsmind.knowledge.lineage.lineage_node import LineageNode

# Measurement modules
from quantsmind.knowledge.measurement.measurement_record import MeasurementRecord
from quantsmind.knowledge.measurement.measurement_repository import MeasurementRepository
from quantsmind.knowledge.metadata.annotation import Annotation
from quantsmind.knowledge.metadata.attribute import Attribute
from quantsmind.knowledge.metadata.label import Label

# Metadata modules
from quantsmind.knowledge.metadata.metadata import KnowledgeMetadata as Metadata
from quantsmind.knowledge.metadata.property import Property
from quantsmind.knowledge.metadata.tag import Tag

# Observation modules
from quantsmind.knowledge.observation.observation import Observation
from quantsmind.knowledge.observation.observation_record import ObservationRecord
from quantsmind.knowledge.observation.observation_session import ObservationSession
from quantsmind.knowledge.observation.observation_store import ObservationStore
from quantsmind.knowledge.ontology.category import Category
from quantsmind.knowledge.ontology.concept import Concept

# Ontology modules
from quantsmind.knowledge.ontology.ontology import Ontology
from quantsmind.knowledge.ontology.semantic_relation import SemanticRelation
from quantsmind.knowledge.ontology.taxonomy import Taxonomy
from quantsmind.knowledge.ontology.vocabulary import Vocabulary
from quantsmind.knowledge.provenance.audit import AuditLog, AuditRecord
from quantsmind.knowledge.provenance.creator import Creator, CreatorRegistry
from quantsmind.knowledge.provenance.experiment import Experiment, ExperimentRegistry
from quantsmind.knowledge.provenance.history import History, HistoryEntry

# Provenance modules
from quantsmind.knowledge.provenance.provenance import Provenance
from quantsmind.knowledge.provenance.source import Source, SourceRegistry
from quantsmind.knowledge.provenance.workflow import Workflow
from quantsmind.knowledge.quality.completeness import Completeness
from quantsmind.knowledge.quality.consistency import Consistency
from quantsmind.knowledge.quality.freshness import Freshness

# Quality modules
from quantsmind.knowledge.quality.quality_rule import QualityRule
from quantsmind.knowledge.quality.uniqueness import Uniqueness
from quantsmind.knowledge.quality.validity import Validity
from quantsmind.knowledge.reasoning.explanation_engine import ExplanationEngine
from quantsmind.knowledge.reasoning.inference_engine import InferenceEngine
from quantsmind.knowledge.reasoning.prediction_engine import PredictionEngine

# Reasoning modules
from quantsmind.knowledge.reasoning.reasoner import Reasoner
from quantsmind.knowledge.reasoning.rule_engine import RuleEngine
from quantsmind.knowledge.repository.knowledge_repository import KnowledgeRepository

# Repository modules
from quantsmind.knowledge.repository.repository import Repository
from quantsmind.knowledge.schema.datatype import DataType as SchemaDataType
from quantsmind.knowledge.schema.field import Field

# Schema modules
from quantsmind.knowledge.schema.schema import Schema
from quantsmind.knowledge.schema.schema_validator import SchemaValidator
from quantsmind.knowledge.search.graph_search import GraphSearch

# Search modules
from quantsmind.knowledge.search.search_engine import SearchEngine
from quantsmind.knowledge.search.semantic_search import SemanticSearch
from quantsmind.knowledge.search.similarity_search import SimilaritySearch

# Serialization modules
from quantsmind.knowledge.serialization.serializers import Serializer, SerializerRegistry
from quantsmind.knowledge.transformation.converter import Converter, ConverterRegistry
from quantsmind.knowledge.transformation.mapper import Mapper
from quantsmind.knowledge.transformation.pipeline import Pipeline

# Transformation modules
from quantsmind.knowledge.transformation.transformation import Transformation

# Validation modules
from quantsmind.knowledge.validation.validators import Validator, ValidatorRegistry

# Versioning modules
from quantsmind.knowledge.versioning.version import Version, VersionHistory

__version__ = "R0.7.0"

__all__ = [
    # Version
    "__version__",
    # Foundational
    "SDK_VERSION",
    "DEFAULT_TIMEOUT",
    "MAX_BATCH_SIZE",
    "DataType",
    "EvidenceType",
    "IndexType",
    "OntologyType",
    "ProvenanceType",
    "QualityType",
    "ReasoningType",
    "RepositoryType",
    "SchemaType",
    "SearchType",
    "SerializationType",
    "TransformationType",
    "ValidationType",
    "VersionType",
    "KnowledgeError",
    "DatasetError",
    "DatasourceError",
    "OntologyError",
    "SchemaError",
    "GraphError",
    "ProvenanceError",
    "LineageError",
    "ObservationError",
    "MeasurementError",
    "QualityError",
    "TransformationError",
    "IndexError",
    "SearchError",
    "RepositoryError",
    "ReasoningError",
    "EvidenceError",
    "ValidationError",
    "SerializationError",
    "VersionError",
    # Dataset
    "Dataset",
    "ScientificDataset",
    "QuantumDataset",
    "TensorDataset",
    "ImageDataset",
    "GraphDataset",
    "SimulationDataset",
    "DatasetRegistry",
    # Datasource
    "DataSource",
    "FileSource",
    "DatabaseSource",
    "StreamSource",
    "APISource",
    # Metadata
    "Metadata",
    "Annotation",
    "Tag",
    "Label",
    "Property",
    "Attribute",
    # Schema
    "Schema",
    "Field",
    "SchemaDataType",
    "SchemaValidator",
    # Ontology
    "Ontology",
    "Concept",
    "Category",
    "Taxonomy",
    "Vocabulary",
    "SemanticRelation",
    # Graph
    "KnowledgeGraph",
    "EntityGraph",
    "RelationshipGraph",
    "SemanticGraph",
    "DependencyGraph",
    # Provenance
    "Provenance",
    "Source",
    "SourceRegistry",
    "Creator",
    "CreatorRegistry",
    "Experiment",
    "ExperimentRegistry",
    "Workflow",
    "History",
    "HistoryEntry",
    "AuditLog",
    "AuditRecord",
    # Lineage
    "Lineage",
    "LineageNode",
    "LineageEdge",
    # Observation
    "Observation",
    "ObservationRecord",
    "ObservationSession",
    "ObservationStore",
    # Measurement
    "MeasurementRecord",
    "MeasurementRepository",
    # Quality
    "QualityRule",
    "Completeness",
    "Consistency",
    "Validity",
    "Freshness",
    "Uniqueness",
    # Transformation
    "Transformation",
    "Pipeline",
    "Mapper",
    "Converter",
    "ConverterRegistry",
    # Indexing
    "Index",
    "GraphIndex",
    "SemanticIndex",
    # Search
    "SearchEngine",
    "SemanticSearch",
    "GraphSearch",
    "SimilaritySearch",
    # Repository
    "Repository",
    "KnowledgeRepository",
    # Reasoning
    "Reasoner",
    "InferenceEngine",
    "RuleEngine",
    "ExplanationEngine",
    "PredictionEngine",
    # Evidence
    "Evidence",
    "Hypothesis",
    "Theory",
    "Law",
    "Fact",
    "EvidenceRule",
    # Validation
    "Validator",
    "ValidatorRegistry",
    # Serialization
    "Serializer",
    "SerializerRegistry",
    # Versioning
    "Version",
    "VersionHistory",
]
