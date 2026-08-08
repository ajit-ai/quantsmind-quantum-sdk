"""
Knowledge Enumerations Module

This module provides enumerations for the Knowledge package.

Purpose
-------
Define domain-specific enumerations for knowledge management.

Responsibilities
----------------
- Define dataset type enumerations
- Define metadata type enumerations
- Define ontology type enumerations
- Define graph type enumerations
- Define provenance type enumerations
- Define reasoning type enumerations
- Define quality type enumerations
- Define search type enumerations
- Define transformation type enumerations
- Define evidence type enumerations

Dependencies
------------
enum (standard library)
"""

from __future__ import annotations

from enum import Enum


class DatasetType(Enum):
    """Dataset type enumeration.

    Defines the types of datasets supported by the knowledge framework.

    Values:
        STRUCTURED: Structured/tabular data
        TIME_SERIES: Time-series data
        SCIENTIFIC: Scientific measurement data
        TENSOR: Multi-dimensional tensor data
        QUANTUM: Quantum state data
        IMAGE: Image data
        GRAPH: Graph/network data
        SIMULATION: Simulation output data
        STREAM: Streaming data
        UNSTRUCTURED: Unstructured data

    Example:
        >>> dtype = DatasetType.STRUCTURED
    """

    STRUCTURED = "structured"
    TIME_SERIES = "time_series"
    SCIENTIFIC = "scientific"
    TENSOR = "tensor"
    QUANTUM = "quantum"
    IMAGE = "image"
    GRAPH = "graph"
    SIMULATION = "simulation"
    STREAM = "stream"
    UNSTRUCTURED = "unstructured"


class MetadataType(Enum):
    """Metadata type enumeration.

    Defines the types of metadata supported.

    Values:
        TAG: Simple tag metadata
        LABEL: Classification label
        ANNOTATION: Rich annotation
        PROPERTY: Property metadata
        ATTRIBUTE: Attribute metadata
        CITATION: Scientific citation
        OWNERSHIP: Ownership information
        TEMPORAL: Temporal metadata
        SPATIAL: Spatial metadata
        CUSTOM: Custom metadata

    Example:
        >>> mtype = MetadataType.TAG
    """

    TAG = "tag"
    LABEL = "label"
    ANNOTATION = "annotation"
    PROPERTY = "property"
    ATTRIBUTE = "attribute"
    CITATION = "citation"
    OWNERSHIP = "ownership"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    CUSTOM = "custom"


class OntologyType(Enum):
    """Ontology type enumeration.

    Defines the types of ontology components.

    Values:
        CONCEPT: Concept entity
        CATEGORY: Category classification
        TAXONOMY: Taxonomy hierarchy
        VOCABULARY: Vocabulary set
        RELATION: Semantic relation
        PROPERTY: Ontology property
        AXIOM: Ontology axiom
        RULE: Ontology rule

    Example:
        >>> otype = OntologyType.CONCEPT
    """

    CONCEPT = "concept"
    CATEGORY = "category"
    TAXONOMY = "taxonomy"
    VOCABULARY = "vocabulary"
    RELATION = "relation"
    PROPERTY = "property"
    AXIOM = "axiom"
    RULE = "rule"


class GraphType(Enum):
    """Graph type enumeration.

    Defines the types of graphs supported.

    Values:
        KNOWLEDGE: Knowledge graph
        ENTITY: Entity graph
        RELATIONSHIP: Relationship graph
        SEMANTIC: Semantic graph
        DEPENDENCY: Dependency graph
        PROVENANCE: Provenance graph
        LINEAGE: Lineage graph
        TEMPORAL: Temporal graph
        SPATIAL: Spatial graph
        HIERARCHICAL: Hierarchical graph

    Example:
        >>> gtype = GraphType.KNOWLEDGE
    """

    KNOWLEDGE = "knowledge"
    ENTITY = "entity"
    RELATIONSHIP = "relationship"
    SEMANTIC = "semantic"
    DEPENDENCY = "dependency"
    PROVENANCE = "provenance"
    LINEAGE = "lineage"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    HIERARCHICAL = "hierarchical"


class ProvenanceType(Enum):
    """Provenance type enumeration.

    Defines the types of provenance information.

    Values:
        SOURCE: Data source
        CREATOR: Creator information
        EXPERIMENT: Experiment context
        WORKFLOW: Workflow execution
        HISTORY: Historical record
        AUDIT: Audit trail
        TRANSFORMATION: Data transformation
        DERIVATION: Data derivation

    Example:
        >>> ptype = ProvenanceType.SOURCE
    """

    SOURCE = "source"
    CREATOR = "creator"
    EXPERIMENT = "experiment"
    WORKFLOW = "workflow"
    HISTORY = "history"
    AUDIT = "audit"
    TRANSFORMATION = "transformation"
    DERIVATION = "derivation"


class ReasoningType(Enum):
    """Reasoning type enumeration.

    Defines the types of reasoning supported.

    Values:
        RULE_BASED: Rule-based reasoning
        SYMBOLIC: Symbolic reasoning
        GRAPH: Graph reasoning
        INDUCTIVE: Inductive reasoning
        DEDUCTIVE: Deductive reasoning
        ABDUCTIVE: Abductive reasoning
        ANALOGICAL: Analogical reasoning
        CAUSAL: Causal reasoning
        PROBABILISTIC: Probabilistic reasoning
        HYBRID: Hybrid reasoning

    Example:
        >>> rtype = ReasoningType.RULE_BASED
    """

    RULE_BASED = "rule_based"
    SYMBOLIC = "symbolic"
    GRAPH = "graph"
    INDUCTIVE = "inductive"
    DEDUCTIVE = "deductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"
    CAUSAL = "causal"
    PROBABILISTIC = "probabilistic"
    HYBRID = "hybrid"


class QualityType(Enum):
    """Quality type enumeration.

    Defines the types of quality checks.

    Values:
        COMPLETENESS: Data completeness
        CONSISTENCY: Data consistency
        VALIDITY: Data validity
        FRESHNESS: Data freshness
        UNIQUENESS: Data uniqueness
        ACCURACY: Data accuracy
        INTEGRITY: Data integrity
        CONFIDENCE: Data confidence

    Example:
        >>> qtype = QualityType.COMPLETENESS
    """

    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    VALIDITY = "validity"
    FRESHNESS = "freshness"
    UNIQUENESS = "uniqueness"
    ACCURACY = "accuracy"
    INTEGRITY = "integrity"
    CONFIDENCE = "confidence"


class SearchType(Enum):
    """Search type enumeration.

    Defines the types of search supported.

    Values:
        SEMANTIC: Semantic search
        GRAPH: Graph search
        SIMILARITY: Similarity search
        FULL_TEXT: Full-text search
        METADATA: Metadata search
        HYBRID: Hybrid search
        FUZZY: Fuzzy search
        VECTOR: Vector search

    Example:
        >>> stype = SearchType.SEMANTIC
    """

    SEMANTIC = "semantic"
    GRAPH = "graph"
    SIMILARITY = "similarity"
    FULL_TEXT = "full_text"
    METADATA = "metadata"
    HYBRID = "hybrid"
    FUZZY = "fuzzy"
    VECTOR = "vector"


class TransformationType(Enum):
    """Transformation type enumeration.

    Defines the types of transformations supported.

    Values:
        MAPPING: Data mapping
        CONVERSION: Data conversion
        AGGREGATION: Data aggregation
        FILTERING: Data filtering
        NORMALIZATION: Data normalization
        ENRICHMENT: Data enrichment
        DERIVATION: Data derivation
        CLEANING: Data cleaning

    Example:
        >>> ttype = TransformationType.MAPPING
    """

    MAPPING = "mapping"
    CONVERSION = "conversion"
    AGGREGATION = "aggregation"
    FILTERING = "filtering"
    NORMALIZATION = "normalization"
    ENRICHMENT = "enrichment"
    DERIVATION = "derivation"
    CLEANING = "cleaning"


class EvidenceType(Enum):
    """Evidence type enumeration.

    Defines the types of evidence supported.

    Values:
        FACT: Factual evidence
        OBSERVATION: Observational evidence
        MEASUREMENT: Measurement evidence
        EXPERIMENT: Experimental evidence
        THEORY: Theoretical evidence
        HYPOTHESIS: Hypothetical evidence
        LAW: Scientific law
        RULE: Rule-based evidence
        DERIVATION: Derived evidence
        TESTIMONY: Testimonial evidence

    Example:
        >>> etype = EvidenceType.FACT
    """

    FACT = "fact"
    OBSERVATION = "observation"
    MEASUREMENT = "measurement"
    EXPERIMENT = "experiment"
    THEORY = "theory"
    HYPOTHESIS = "hypothesis"
    LAW = "law"
    RULE = "rule"
    DERIVATION = "derivation"
    TESTIMONY = "testimony"


class DataSourceType(Enum):
    """Data source type enumeration.

    Defines the types of data sources.

    Values:
        FILE: File-based source
        DATABASE: Database source
        STREAM: Streaming source
        API: API-based source
        MEMORY: In-memory source
        DISTRIBUTED: Distributed source
        CLOUD: Cloud storage source
        CUSTOM: Custom source

    Example:
        >>> dstype = DataSourceType.FILE
    """

    FILE = "file"
    DATABASE = "database"
    STREAM = "stream"
    API = "api"
    MEMORY = "memory"
    DISTRIBUTED = "distributed"
    CLOUD = "cloud"
    CUSTOM = "custom"


class SerializationFormat(Enum):
    """Serialization format enumeration.

    Defines the serialization formats supported.

    Values:
        JSON: JSON format
        YAML: YAML format
        TOML: TOML format
        MESSAGE_PACK: MessagePack format
        PROTOBUF: Protocol Buffers
        PICKLE: Python pickle
        CSV: CSV format
        PARQUET: Parquet format
        RDF: RDF format
        JSON_LD: JSON-LD format

    Example:
        >>> sformat = SerializationFormat.JSON
    """

    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    MESSAGE_PACK = "msgpack"
    PROTOBUF = "protobuf"
    PICKLE = "pickle"
    CSV = "csv"
    PARQUET = "parquet"
    RDF = "rdf"
    JSON_LD = "json_ld"


# Export
__all__ = [
    "DatasetType",
    "MetadataType",
    "OntologyType",
    "GraphType",
    "ProvenanceType",
    "ReasoningType",
    "QualityType",
    "SearchType",
    "TransformationType",
    "EvidenceType",
    "DataSourceType",
    "SerializationFormat",
]
