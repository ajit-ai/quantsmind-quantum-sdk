"""
Knowledge Protocols Module

This module provides structural subtyping protocols for the Knowledge package.

Purpose
-------
Define protocols for structural subtyping in knowledge management.

Responsibilities
----------------
- Define dataset protocols
- Define metadata protocols
- Define ontology protocols
- Define graph protocols
- Define provenance protocols
- Define reasoning protocols
- Define repository protocols
- Define search protocols
- Define transformation protocols
- Define validation protocols

Dependencies
------------
typing (standard library)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable

from quantsmind.knowledge.types import (
    DatasetData,
    DatasetID,
    DatasetSchema,
    EdgeData,
    Explanation,
    GraphID,
    InferenceID,
    KnowledgeItemData,
    KnowledgeItemID,
    MetadataDict,
    NodeData,
    Path,
    Prediction,
    ProvenanceChain,
    SearchQuery,
    SearchResults,
    SerializedData,
    ValidationResult,
)


@runtime_checkable
class DatasetProtocol(Protocol):
    """Protocol for dataset implementations.

    This protocol defines the structural contract for dataset classes.

    Example:
        >>> def process_dataset(dataset: DatasetProtocol) -> None:
        ...     # Process dataset
        ...     pass
    """

    @property
    def id(self) -> DatasetID: ...

    @property
    def name(self) -> str: ...

    @property
    def schema(self) -> DatasetSchema: ...

    @property
    def data(self) -> DatasetData: ...

    @property
    def size(self) -> int: ...

    def add_record(self, record: dict[str, Any]) -> None: ...

    def get_record(self, record_id: str) -> dict[str, Any] | None: ...

    def query(self, query: dict[str, Any]) -> list[dict[str, Any]]: ...

    def validate(self) -> ValidationResult: ...


@runtime_checkable
class MetadataProtocol(Protocol):
    """Protocol for metadata implementations.

    This protocol defines the structural contract for metadata classes.

    Example:
        >>> def process_metadata(metadata: MetadataProtocol) -> None:
        ...     # Process metadata
        ...     pass
    """

    def get(self, key: str, default: Any = None) -> Any: ...

    def set(self, key: str, value: Any) -> None: ...

    def update(self, data: MetadataDict) -> None: ...

    def delete(self, key: str) -> bool: ...

    def has(self, key: str) -> bool: ...

    def keys(self) -> list[str]: ...

    def values(self) -> list[Any]: ...

    def items(self) -> list[tuple[str, Any]]: ...

    def to_dict(self) -> MetadataDict: ...


@runtime_checkable
class OntologyProtocol(Protocol):
    """Protocol for ontology implementations.

    This protocol defines the structural contract for ontology classes.

    Example:
        >>> def process_ontology(ontology: OntologyProtocol) -> None:
        ...     # Process ontology
        ...     pass
    """

    def add_concept(self, concept_id: str, concept_data: dict[str, Any]) -> None: ...

    def get_concept(self, concept_id: str) -> dict[str, Any] | None: ...

    def add_relation(self, source: str, relation: str, target: str) -> None: ...

    def get_relations(self, concept_id: str) -> list[tuple[str, str]]: ...

    def traverse(self, start: str, max_depth: int = 3) -> list[str]: ...

    def validate(self) -> ValidationResult: ...


@runtime_checkable
class GraphProtocol(Protocol):
    """Protocol for graph implementations.

    This protocol defines the structural contract for graph classes.

    Example:
        >>> def process_graph(graph: GraphProtocol) -> None:
        ...     # Process graph
        ...     pass
    """

    @property
    def id(self) -> GraphID: ...

    def add_node(self, node_id: str, data: NodeData | None = None) -> None: ...

    def add_edge(self, source: str, target: str, data: EdgeData | None = None) -> None: ...

    def get_node(self, node_id: str) -> NodeData | None: ...

    def get_edge(self, source: str, target: str) -> EdgeData | None: ...

    def neighbors(self, node_id: str) -> list[str]: ...

    def shortest_path(self, source: str, target: str) -> Path | None: ...

    def traverse(self, start: str, max_depth: int = 3) -> list[str]: ...


@runtime_checkable
class ProvenanceProtocol(Protocol):
    """Protocol for provenance implementations.

    This protocol defines the structural contract for provenance classes.

    Example:
        >>> def process_provenance(provenance: ProvenanceProtocol) -> None:
        ...     # Process provenance
        ...     pass
    """

    def record_origin(self, data_id: str, source: str, metadata: dict[str, Any] | None = None) -> None: ...

    def get_provenance(self, data_id: str) -> ProvenanceChain | None: ...

    def trace_lineage(self, data_id: str) -> list[str]: ...

    def add_transformation(self, data_id: str, transformation: str, input_ids: list[str]) -> None: ...

    def validate(self) -> ValidationResult: ...


@runtime_checkable
class ReasonerProtocol(Protocol):
    """Protocol for reasoner implementations.

    This protocol defines the structural contract for reasoner classes.

    Example:
        >>> def process_reasoner(reasoner: ReasonerProtocol) -> None:
        ...     # Process reasoner
        ...     pass
    """

    def infer(self, facts: list[dict[str, Any]], query: str) -> InferenceID: ...

    def explain(self, inference_id: InferenceID) -> Explanation: ...

    def predict(self, context: dict[str, Any]) -> Prediction: ...

    def add_rule(self, rule: dict[str, Any]) -> None: ...

    def validate(self) -> ValidationResult: ...


@runtime_checkable
class RepositoryProtocol(Protocol):
    """Protocol for repository implementations.

    This protocol defines the structural contract for repository classes.

    Example:
        >>> def process_repository(repository: RepositoryProtocol) -> None:
        ...     # Process repository
        ...     pass
    """

    def store(self, item_id: KnowledgeItemID, data: KnowledgeItemData) -> None: ...

    def retrieve(self, item_id: KnowledgeItemID) -> KnowledgeItemData | None: ...

    def search(self, query: SearchQuery) -> SearchResults: ...

    def delete(self, item_id: KnowledgeItemID) -> bool: ...

    def update(self, item_id: KnowledgeItemID, data: KnowledgeItemData) -> bool: ...

    def exists(self, item_id: KnowledgeItemID) -> bool: ...


@runtime_checkable
class SearchEngineProtocol(Protocol):
    """Protocol for search engine implementations.

    This protocol defines the structural contract for search engine classes.

    Example:
        >>> def process_search_engine(search_engine: SearchEngineProtocol) -> None:
        ...     # Process search engine
        ...     pass
    """

    def index(self, doc_id: str, document: dict[str, Any]) -> None: ...

    def search(self, query: SearchQuery, limit: int = 10) -> SearchResults: ...

    def remove(self, doc_id: str) -> bool: ...

    def update(self, doc_id: str, document: dict[str, Any]) -> bool: ...

    def get_index_stats(self) -> dict[str, Any]: ...


@runtime_checkable
class TransformerProtocol(Protocol):
    """Protocol for transformer implementations.

    This protocol defines the structural contract for transformer classes.

    Example:
        >>> def process_transformer(transformer: TransformerProtocol) -> None:
        ...     # Process transformer
        ...     pass
    """

    def transform(self, data: Any) -> Any: ...

    def apply(self, data: list[Any]) -> list[Any]: ...

    def compose(self, other: TransformerProtocol) -> TransformerProtocol: ...

    def validate(self) -> ValidationResult: ...


@runtime_checkable
class ValidatorProtocol(Protocol):
    """Protocol for validator implementations.

    This protocol defines the structural contract for validator classes.

    Example:
        >>> def process_validator(validator: ValidatorProtocol) -> None:
        ...     # Process validator
        ...     pass
    """

    def validate(self, data: Any) -> ValidationResult: ...

    def add_rule(self, rule: Callable[[Any], ValidationResult]) -> None: ...

    def remove_rule(self, rule_name: str) -> bool: ...

    def get_rules(self) -> list[str]: ...

    def validate_schema(self, schema: dict[str, Any], data: Any) -> ValidationResult: ...


@runtime_checkable
class SerializerProtocol(Protocol):
    """Protocol for serializer implementations.

    This protocol defines the structural contract for serializer classes.

    Example:
        >>> def process_serializer(serializer: SerializerProtocol) -> None:
        ...     # Process serializer
        ...     pass
    """

    def serialize(self, data: Any) -> SerializedData: ...

    def deserialize(self, data: SerializedData) -> Any: ...

    def get_format(self) -> str: ...

    def validate(self) -> ValidationResult: ...


@runtime_checkable
class ObservableProtocol(Protocol):
    """Protocol for observable implementations.

    This protocol defines the structural contract for observable classes.

    Example:
        >>> def process_observable(observable: ObservableProtocol) -> None:
        ...     # Process observable
        ...     pass
    """

    def register_observer(self, observer: Any) -> None: ...

    def unregister_observer(self, observer: Any) -> None: ...

    def notify_observers(self, event: str, data: dict[str, Any] | None = None) -> None: ...


@runtime_checkable
class IndexableProtocol(Protocol):
    """Protocol for indexable implementations.

    This protocol defines the structural contract for indexable classes.

    Example:
        >>> def process_indexable(indexable: IndexableProtocol) -> None:
        ...     # Process indexable
        ...     pass
    """

    def get_index_keys(self) -> list[str]: ...

    def get_index_value(self, key: str) -> Any: ...

    def set_index_value(self, key: str, value: Any) -> None: ...


@runtime_checkable
class VersionableProtocol(Protocol):
    """Protocol for versionable implementations.

    This protocol defines the structural contract for versionable classes.

    Example:
        >>> def process_versionable(versionable: VersionableProtocol) -> None:
        ...     # Process versionable
        ...     pass
    """

    def get_version(self) -> str: ...

    def set_version(self, version: str) -> None: ...

    def get_version_history(self) -> list[str]: ...


@runtime_checkable
class TraceableProtocol(Protocol):
    """Protocol for traceable implementations.

    This protocol defines the structural contract for traceable classes.

    Example:
        >>> def process_traceable(traceable: TraceableProtocol) -> None:
        ...     # Process traceable
        ...     pass
    """

    def get_trace_id(self) -> str: ...

    def get_trace_chain(self) -> list[str]: ...

    def add_trace_step(self, step: str) -> None: ...


@runtime_checkable
class QueryableProtocol(Protocol):
    """Protocol for queryable implementations.

    This protocol defines the structural contract for queryable classes.

    Example:
        >>> def process_queryable(queryable: QueryableProtocol) -> None:
        ...     # Process queryable
        ...     pass
    """

    def query(self, query: dict[str, Any]) -> list[dict[str, Any]]: ...

    def count(self, query: dict[str, Any]) -> int: ...

    def aggregate(self, query: dict[str, Any], field: str) -> dict[str, Any]: ...


@runtime_checkable
class TransformableProtocol(Protocol):
    """Protocol for transformable implementations.

    This protocol defines the structural contract for transformable classes.

    Example:
        >>> def process_transformable(transformable: TransformableProtocol) -> None:
        ...     # Process transformable
        ...     pass
    """

    def apply_transformation(self, transformation: Callable[[Any], Any]) -> Any: ...

    def get_transformation_history(self) -> list[str]: ...


@runtime_checkable
class SerializableProtocol(Protocol):
    """Protocol for serializable implementations.

    This protocol defines the structural contract for serializable classes.

    Example:
        >>> def process_serializable(serializable: SerializableProtocol) -> None:
        ...     # Process serializable
        ...     pass
    """

    def serialize(self) -> SerializedData: ...

    def deserialize(self, data: SerializedData) -> None: ...

    def to_dict(self) -> dict[str, Any]: ...

    def from_dict(self, data: dict[str, Any]) -> None: ...


@runtime_checkable
class ValidatableProtocol(Protocol):
    """Protocol for validatable implementations.

    This protocol defines the structural contract for validatable classes.

    Example:
        >>> def process_validatable(validatable: ValidatableProtocol) -> None:
        ...     # Process validatable
        ...     pass
    """

    def validate(self) -> ValidationResult: ...

    def get_validation_errors(self) -> list[str]: ...

    def is_valid(self) -> bool: ...


@runtime_checkable
class ClonableProtocol(Protocol):
    """Protocol for clonable implementations.

    This protocol defines the structural contract for clonable classes.

    Example:
        >>> def process_clonable(clonable: ClonableProtocol) -> None:
        ...     # Process clonable
        ...     pass
    """

    def clone(self) -> Any: ...

    def deep_clone(self) -> Any: ...


@runtime_checkable
class MergeableProtocol(Protocol):
    """Protocol for mergeable implementations.

    This protocol defines the structural contract for mergeable classes.

    Example:
        >>> def process_mergeable(mergeable: MergeableProtocol) -> None:
        ...     # Process mergeable
        ...     pass
    """

    def merge(self, other: Any) -> Any: ...

    def merge_with_conflict_resolution(self, other: Any, resolver: Callable[[Any, Any], Any]) -> Any: ...


@runtime_checkable
class ComparableProtocol(Protocol):
    """Protocol for comparable implementations.

    This protocol defines the structural contract for comparable classes.

    Example:
        >>> def process_comparable(comparable: ComparableProtocol) -> None:
        ...     # Process comparable
        ...     pass
    """

    def compare(self, other: Any) -> int: ...

    def equals(self, other: Any) -> bool: ...

    def is_less_than(self, other: Any) -> bool: ...

    def is_greater_than(self, other: Any) -> bool: ...


# Export
__all__ = [
    "DatasetProtocol",
    "MetadataProtocol",
    "OntologyProtocol",
    "GraphProtocol",
    "ProvenanceProtocol",
    "ReasonerProtocol",
    "RepositoryProtocol",
    "SearchEngineProtocol",
    "TransformerProtocol",
    "ValidatorProtocol",
    "SerializerProtocol",
    "ObservableProtocol",
    "IndexableProtocol",
    "VersionableProtocol",
    "TraceableProtocol",
    "QueryableProtocol",
    "TransformableProtocol",
    "SerializableProtocol",
    "ValidatableProtocol",
    "ClonableProtocol",
    "MergeableProtocol",
    "ComparableProtocol",
]
