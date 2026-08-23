"""
Knowledge Interfaces Module

This module provides abstract interfaces for the Knowledge package.

Purpose
-------
Define abstract interfaces for knowledge management components.

Responsibilities
----------------
- Define dataset interfaces
- Define metadata interfaces
- Define ontology interfaces
- Define graph interfaces
- Define provenance interfaces
- Define reasoning interfaces
- Define repository interfaces
- Define search interfaces
- Define transformation interfaces
- Define validation interfaces

Dependencies
------------
typing (standard library)
abc (standard library)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

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


class IDataset(ABC):
    """Interface for dataset implementations.

    This interface defines the contract for dataset classes.

    Methods:
        id: Get dataset ID
        name: Get dataset name
        schema: Get dataset schema
        data: Get dataset data
        size: Get dataset size
        add_record: Add a record to the dataset
        get_record: Get a record from the dataset
        query: Query the dataset
        validate: Validate the dataset

    Example:
        >>> class MyDataset(IDataset):
        ...     # Implementation
        ...     pass
    """

    @abstractmethod
    @property
    def id(self) -> DatasetID:
        """Get the dataset ID.

        Returns:
            Dataset ID

        Example:
            >>> dataset_id = dataset.id
        """
        pass

    @abstractmethod
    @property
    def name(self) -> str:
        """Get the dataset name.

        Returns:
            Dataset name

        Example:
            >>> dataset_name = dataset.name
        """
        pass

    @abstractmethod
    @property
    def schema(self) -> DatasetSchema:
        """Get the dataset schema.

        Returns:
            Dataset schema

        Example:
            >>> schema = dataset.schema
        """
        pass

    @abstractmethod
    @property
    def data(self) -> DatasetData:
        """Get the dataset data.

        Returns:
            Dataset data

        Example:
            >>> data = dataset.data
        """
        pass

    @abstractmethod
    @property
    def size(self) -> int:
        """Get the dataset size.

        Returns:
            Dataset size

        Example:
            >>> size = dataset.size
        """
        pass

    @abstractmethod
    def add_record(self, record: dict[str, Any]) -> None:
        """Add a record to the dataset.

        Args:
            record: Record to add

        Example:
            >>> dataset.add_record({"key": "value"})
        """
        pass

    @abstractmethod
    def get_record(self, record_id: str) -> dict[str, Any] | None:
        """Get a record from the dataset.

        Args:
            record_id: Record ID

        Returns:
            Record or None

        Example:
            >>> record = dataset.get_record("rec_001")
        """
        pass

    @abstractmethod
    def query(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        """Query the dataset.

        Args:
            query: Query parameters

        Returns:
            Query results

        Example:
            >>> results = dataset.query({"key": "value"})
        """
        pass

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Validate the dataset.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = dataset.validate()
        """
        pass


class IMetadata(ABC):
    """Interface for metadata implementations.

    This interface defines the contract for metadata classes.

    Methods:
        get: Get metadata value
        set: Set metadata value
        update: Update metadata
        delete: Delete metadata value
        has: Check if metadata key exists
        keys: Get all keys
        values: Get all values
        items: Get all items
        to_dict: Convert to dictionary

    Example:
        >>> class MyMetadata(IMetadata):
        ...     # Implementation
        ...     pass
    """

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get a metadata value.

        Args:
            key: Metadata key
            default: Default value

        Returns:
            Metadata value or default

        Example:
            >>> value = metadata.get("key")
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Set a metadata value.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> metadata.set("key", "value")
        """
        pass

    @abstractmethod
    def update(self, data: MetadataDict) -> None:
        """Update metadata.

        Args:
            data: Metadata data

        Example:
            >>> metadata.update({"key": "value"})
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a metadata value.

        Args:
            key: Metadata key

        Returns:
            True if deleted

        Example:
            >>> deleted = metadata.delete("key")
        """
        pass

    @abstractmethod
    def has(self, key: str) -> bool:
        """Check if metadata key exists.

        Args:
            key: Metadata key

        Returns:
            True if key exists

        Example:
            >>> if metadata.has("key"):
            ...     print("Key exists")
        """
        pass

    @abstractmethod
    def keys(self) -> list[str]:
        """Get all metadata keys.

        Returns:
            List of keys

        Example:
            >>> keys = metadata.keys()
        """
        pass

    @abstractmethod
    def values(self) -> list[Any]:
        """Get all metadata values.

        Returns:
            List of values

        Example:
            >>> values = metadata.values()
        """
        pass

    @abstractmethod
    def items(self) -> list[tuple[str, Any]]:
        """Get all metadata items.

        Returns:
            List of (key, value) tuples

        Example:
            >>> items = metadata.items()
        """
        pass

    @abstractmethod
    def to_dict(self) -> MetadataDict:
        """Convert to dictionary.

        Returns:
            Metadata dictionary

        Example:
            >>> data = metadata.to_dict()
        """
        pass


class IOntology(ABC):
    """Interface for ontology implementations.

    This interface defines the contract for ontology classes.

    Methods:
        add_concept: Add a concept
        get_concept: Get a concept
        add_relation: Add a relation
        get_relations: Get relations
        traverse: Traverse ontology
        validate: Validate ontology

    Example:
        >>> class MyOntology(IOntology):
        ...     # Implementation
        ...     pass
    """

    @abstractmethod
    def add_concept(self, concept_id: str, concept_data: dict[str, Any]) -> None:
        """Add a concept to the ontology.

        Args:
            concept_id: Concept ID
            concept_data: Concept data

        Example:
            >>> ontology.add_concept("concept_001", {"name": "Entity"})
        """
        pass

    @abstractmethod
    def get_concept(self, concept_id: str) -> dict[str, Any] | None:
        """Get a concept from the ontology.

        Args:
            concept_id: Concept ID

        Returns:
            Concept data or None

        Example:
            >>> concept = ontology.get_concept("concept_001")
        """
        pass

    @abstractmethod
    def add_relation(self, source: str, relation: str, target: str) -> None:
        """Add a relation to the ontology.

        Args:
            source: Source concept
            relation: Relation type
            target: Target concept

        Example:
            >>> ontology.add_relation("entity", "is_a", "physical_entity")
        """
        pass

    @abstractmethod
    def get_relations(self, concept_id: str) -> list[tuple[str, str]]:
        """Get relations for a concept.

        Args:
            concept_id: Concept ID

        Returns:
            List of (relation, target) tuples

        Example:
            >>> relations = ontology.get_relations("concept_001")
        """
        pass

    @abstractmethod
    def traverse(self, start: str, max_depth: int = 3) -> list[str]:
        """Traverse the ontology.

        Args:
            start: Starting concept
            max_depth: Maximum traversal depth

        Returns:
            List of visited concepts

        Example:
            >>> visited = ontology.traverse("concept_001")
        """
        pass

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Validate the ontology.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = ontology.validate()
        """
        pass


class IGraph(ABC):
    """Interface for graph implementations.

    This interface defines the contract for graph classes.

    Methods:
        id: Get graph ID
        add_node: Add a node
        add_edge: Add an edge
        get_node: Get a node
        get_edge: Get an edge
        neighbors: Get neighbors
        shortest_path: Find shortest path
        traverse: Traverse graph

    Example:
        >>> class MyGraph(IGraph):
        ...     # Implementation
        ...     pass
    """

    @abstractmethod
    @property
    def id(self) -> GraphID:
        """Get the graph ID.

        Returns:
            Graph ID

        Example:
            >>> graph_id = graph.id
        """
        pass

    @abstractmethod
    def add_node(self, node_id: str, data: NodeData | None = None) -> None:
        """Add a node to the graph.

        Args:
            node_id: Node ID
            data: Node data

        Example:
            >>> graph.add_node("node_001", {"label": "Entity"})
        """
        pass

    @abstractmethod
    def add_edge(self, source: str, target: str, data: EdgeData | None = None) -> None:
        """Add an edge to the graph.

        Args:
            source: Source node
            target: Target node
            data: Edge data

        Example:
            >>> graph.add_edge("node_001", "node_002", {"type": "related"})
        """
        pass

    @abstractmethod
    def get_node(self, node_id: str) -> NodeData | None:
        """Get a node from the graph.

        Args:
            node_id: Node ID

        Returns:
            Node data or None

        Example:
            >>> node = graph.get_node("node_001")
        """
        pass

    @abstractmethod
    def get_edge(self, source: str, target: str) -> EdgeData | None:
        """Get an edge from the graph.

        Args:
            source: Source node
            target: Target node

        Returns:
            Edge data or None

        Example:
            >>> edge = graph.get_edge("node_001", "node_002")
        """
        pass

    @abstractmethod
    def neighbors(self, node_id: str) -> list[str]:
        """Get neighbors of a node.

        Args:
            node_id: Node ID

        Returns:
            List of neighbor node IDs

        Example:
            >>> neighbors = graph.neighbors("node_001")
        """
        pass

    @abstractmethod
    def shortest_path(self, source: str, target: str) -> Path | None:
        """Find shortest path between nodes.

        Args:
            source: Source node
            target: Target node

        Returns:
            Path or None

        Example:
            >>> path = graph.shortest_path("node_001", "node_002")
        """
        pass

    @abstractmethod
    def traverse(self, start: str, max_depth: int = 3) -> list[str]:
        """Traverse the graph.

        Args:
            start: Starting node
            max_depth: Maximum traversal depth

        Returns:
            List of visited nodes

        Example:
            >>> visited = graph.traverse("node_001")
        """
        pass


class IProvenance(ABC):
    """Interface for provenance implementations.

    This interface defines the contract for provenance classes.

    Methods:
        record_origin: Record data origin
        get_provenance: Get provenance chain
        trace_lineage: Trace data lineage
        add_transformation: Add transformation record
        validate: Validate provenance

    Example:
        >>> class MyProvenance(IProvenance):
        ...     # Implementation
        ...     pass
    """

    @abstractmethod
    def record_origin(self, data_id: str, source: str, metadata: dict[str, Any] | None = None) -> None:
        """Record data origin.

        Args:
            data_id: Data ID
            source: Data source
            metadata: Additional metadata

        Example:
            >>> provenance.record_origin("data_001", "file_source")
        """
        pass

    @abstractmethod
    def get_provenance(self, data_id: str) -> ProvenanceChain | None:
        """Get provenance chain for data.

        Args:
            data_id: Data ID

        Returns:
            Provenance chain or None

        Example:
            >>> chain = provenance.get_provenance("data_001")
        """
        pass

    @abstractmethod
    def trace_lineage(self, data_id: str) -> list[str]:
        """Trace data lineage.

        Args:
            data_id: Data ID

        Returns:
            List of ancestor data IDs

        Example:
            >>> ancestors = provenance.trace_lineage("data_001")
        """
        pass

    @abstractmethod
    def add_transformation(self, data_id: str, transformation: str, input_ids: list[str]) -> None:
        """Add transformation record.

        Args:
            data_id: Data ID
            transformation: Transformation description
            input_ids: Input data IDs

        Example:
            >>> provenance.add_transformation("data_001", "filter", ["input_001"])
        """
        pass

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Validate provenance.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = provenance.validate()
        """
        pass


class IReasoner(ABC):
    """Interface for reasoner implementations.

    This interface defines the contract for reasoner classes.

    Methods:
        infer: Perform inference
        explain: Generate explanation
        predict: Generate prediction
        add_rule: Add reasoning rule
        validate: Validate reasoning

    Example:
        >>> class MyReasoner(IReasoner):
        ...     # Implementation
        ...     pass
    """

    @abstractmethod
    def infer(self, facts: list[dict[str, Any]], query: str) -> InferenceID:
        """Perform inference.

        Args:
            facts: Known facts
            query: Query to answer

        Returns:
            Inference ID

        Example:
            >>> inference_id = reasoner.infer(facts, "What is X?")
        """
        pass

    @abstractmethod
    def explain(self, inference_id: InferenceID) -> Explanation:
        """Generate explanation for inference.

        Args:
            inference_id: Inference ID

        Returns:
            Explanation

        Example:
            >>> explanation = reasoner.explain(inference_id)
        """
        pass

    @abstractmethod
    def predict(self, context: dict[str, Any]) -> Prediction:
        """Generate prediction.

        Args:
            context: Prediction context

        Returns:
            Prediction

        Example:
            >>> prediction = reasoner.predict({"data": values})
        """
        pass

    @abstractmethod
    def add_rule(self, rule: dict[str, Any]) -> None:
        """Add reasoning rule.

        Args:
            rule: Rule definition

        Example:
            >>> reasoner.add_rule({"if": "X", "then": "Y"})
        """
        pass

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Validate reasoner.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = reasoner.validate()
        """
        pass


class IRepository(ABC):
    """Interface for repository implementations.

    This interface defines the contract for repository classes.

    Methods:
        store: Store knowledge item
        retrieve: Retrieve knowledge item
        search: Search knowledge items
        delete: Delete knowledge item
        update: Update knowledge item
        exists: Check if item exists

    Example:
        >>> class MyRepository(IRepository):
        ...     # Implementation
        ...     pass
    """

    @abstractmethod
    def store(self, item_id: KnowledgeItemID, data: KnowledgeItemData) -> None:
        """Store a knowledge item.

        Args:
            item_id: Item ID
            data: Item data

        Example:
            >>> repository.store("item_001", {"key": "value"})
        """
        pass

    @abstractmethod
    def retrieve(self, item_id: KnowledgeItemID) -> KnowledgeItemData | None:
        """Retrieve a knowledge item.

        Args:
            item_id: Item ID

        Returns:
            Item data or None

        Example:
            >>> data = repository.retrieve("item_001")
        """
        pass

    @abstractmethod
    def search(self, query: SearchQuery) -> SearchResults:
        """Search knowledge items.

        Args:
            query: Search query

        Returns:
            Search results

        Example:
            >>> results = repository.search("entity")
        """
        pass

    @abstractmethod
    def delete(self, item_id: KnowledgeItemID) -> bool:
        """Delete a knowledge item.

        Args:
            item_id: Item ID

        Returns:
            True if deleted

        Example:
            >>> deleted = repository.delete("item_001")
        """
        pass

    @abstractmethod
    def update(self, item_id: KnowledgeItemID, data: KnowledgeItemData) -> bool:
        """Update a knowledge item.

        Args:
            item_id: Item ID
            data: New item data

        Returns:
            True if updated

        Example:
            >>> updated = repository.update("item_001", {"key": "new_value"})
        """
        pass

    @abstractmethod
    def exists(self, item_id: KnowledgeItemID) -> bool:
        """Check if item exists.

        Args:
            item_id: Item ID

        Returns:
            True if exists

        Example:
            >>> if repository.exists("item_001"):
            ...     print("Item exists")
        """
        pass


class ISearchEngine(ABC):
    """Interface for search engine implementations.

    This interface defines the contract for search engine classes.

    Methods:
        index: Index a document
        search: Search documents
        remove: Remove document from index
        update: Update document in index
        get_index_stats: Get index statistics

    Example:
        >>> class MySearchEngine(ISearchEngine):
        ...     # Implementation
        ...     pass
    """

    @abstractmethod
    def index(self, doc_id: str, document: dict[str, Any]) -> None:
        """Index a document.

        Args:
            doc_id: Document ID
            document: Document data

        Example:
            >>> search_engine.index("doc_001", {"text": "content"})
        """
        pass

    @abstractmethod
    def search(self, query: SearchQuery, limit: int = 10) -> SearchResults:
        """Search documents.

        Args:
            query: Search query
            limit: Result limit

        Returns:
            Search results

        Example:
            >>> results = search_engine.search("query", limit=10)
        """
        pass

    @abstractmethod
    def remove(self, doc_id: str) -> bool:
        """Remove document from index.

        Args:
            doc_id: Document ID

        Returns:
            True if removed

        Example:
            >>> removed = search_engine.remove("doc_001")
        """
        pass

    @abstractmethod
    def update(self, doc_id: str, document: dict[str, Any]) -> bool:
        """Update document in index.

        Args:
            doc_id: Document ID
            document: New document data

        Returns:
            True if updated

        Example:
            >>> updated = search_engine.update("doc_001", {"text": "new_content"})
        """
        pass

    @abstractmethod
    def get_index_stats(self) -> dict[str, Any]:
        """Get index statistics.

        Returns:
            Index statistics

        Example:
            >>> stats = search_engine.get_index_stats()
        """
        pass


class ITransformer(ABC):
    """Interface for transformer implementations.

    This interface defines the contract for transformer classes.

    Methods:
        transform: Transform data
        apply: Apply transformation
        compose: Compose transformations
        validate: Validate transformation

    Example:
        >>> class MyTransformer(ITransformer):
        ...     # Implementation
        ...     pass
    """

    @abstractmethod
    def transform(self, data: Any) -> Any:
        """Transform data.

        Args:
            data: Input data

        Returns:
            Transformed data

        Example:
            >>> transformed = transformer.transform(input_data)
        """
        pass

    @abstractmethod
    def apply(self, data: list[Any]) -> list[Any]:
        """Apply transformation to data list.

        Args:
            data: Input data list

        Returns:
            Transformed data list

        Example:
            >>> transformed = transformer.apply([item1, item2])
        """
        pass

    @abstractmethod
    def compose(self, other: ITransformer) -> ITransformer:
        """Compose with another transformer.

        Args:
            other: Other transformer

        Returns:
            Composed transformer

        Example:
            >>> composed = transformer1.compose(transformer2)
        """
        pass

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Validate transformation.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = transformer.validate()
        """
        pass


class IValidator(ABC):
    """Interface for validator implementations.

    This interface defines the contract for validator classes.

    Methods:
        validate: Validate data
        add_rule: Add validation rule
        remove_rule: Remove validation rule
        get_rules: Get validation rules
        validate_schema: Validate schema

    Example:
        >>> class MyValidator(IValidator):
        ...     # Implementation
        ...     pass
    """

    @abstractmethod
    def validate(self, data: Any) -> ValidationResult:
        """Validate data.

        Args:
            data: Data to validate

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate(data)
        """
        pass

    @abstractmethod
    def add_rule(self, rule: Callable[[Any], ValidationResult]) -> None:
        """Add validation rule.

        Args:
            rule: Validation rule

        Example:
            >>> validator.add_rule(lambda x: (True, []))
        """
        pass

    @abstractmethod
    def remove_rule(self, rule_name: str) -> bool:
        """Remove validation rule.

        Args:
            rule_name: Rule name

        Returns:
            True if removed

        Example:
            >>> removed = validator.remove_rule("rule_001")
        """
        pass

    @abstractmethod
    def get_rules(self) -> list[str]:
        """Get validation rules.

        Returns:
            List of rule names

        Example:
            >>> rules = validator.get_rules()
        """
        pass

    @abstractmethod
    def validate_schema(self, schema: dict[str, Any], data: Any) -> ValidationResult:
        """Validate against schema.

        Args:
            schema: Schema definition
            data: Data to validate

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = validator.validate_schema(schema, data)
        """
        pass


class ISerializer(ABC):
    """Interface for serializer implementations.

    This interface defines the contract for serializer classes.

    Methods:
        serialize: Serialize data
        deserialize: Deserialize data
        get_format: Get serialization format
        validate: Validate serialization

    Example:
        >>> class MySerializer(ISerializer):
        ...     # Implementation
        ...     pass
    """

    @abstractmethod
    def serialize(self, data: Any) -> SerializedData:
        """Serialize data.

        Args:
            data: Data to serialize

        Returns:
            Serialized data

        Example:
            >>> serialized = serializer.serialize(data)
        """
        pass

    @abstractmethod
    def deserialize(self, data: SerializedData) -> Any:
        """Deserialize data.

        Args:
            data: Data to deserialize

        Returns:
            Deserialized data

        Example:
            >>> deserialized = serializer.deserialize(serialized_data)
        """
        pass

    @abstractmethod
    def get_format(self) -> str:
        """Get serialization format.

        Returns:
            Format name

        Example:
            >>> format = serializer.get_format()
        """
        pass

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Validate serializer.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = serializer.validate()
        """
        pass


# Export
__all__ = [
    "IDataset",
    "IMetadata",
    "IOntology",
    "IGraph",
    "IProvenance",
    "IReasoner",
    "IRepository",
    "ISearchEngine",
    "ITransformer",
    "IValidator",
    "ISerializer",
]
