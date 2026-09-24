# Knowledge Foundations

## Overview

Knowledge representation in `quantsmind.knowledge`: value types,
provenance records, validation helpers, and a concrete `KnowledgeGraph`
with neighbors, degrees, and shortest paths.

## Purpose

Let users model entities and relationships as inspectable graph data
with provenance attached, without any external store.

## Concept

Graphs hold node/edge dicts; `neighbors()`, `degree()`, and
`shortest_path()` traverse them; `SearchResult` and
`KnowledgeValidator` cover retrieval vocabulary and strictness-gated
validation.

## API

`KnowledgeGraph` (add/remove nodes and edges, traversal),
`SearchResult`, `KnowledgeValidator`, package enums, exceptions, and
constants. Abstract engines (`SearchEngine`, repositories) define
extension seams and are not directly instantiable.

## Input / Processing / Output

Input: node ids, edge pairs, strictness levels. Processing: dict
traversal. Output: neighbor lists, paths, validation verdicts.

## Example

```python
from quantsmind.knowledge.graph.knowledge_graph import KnowledgeGraph

graph = KnowledgeGraph("g1")
graph.add_node("a")
graph.add_node("b")
graph.add_edge("a", "b")
assert graph.shortest_path("a", "b") == ["a", "b"]
```

## Limitations

In-memory dict storage only; no persistent backend; search backends
beyond the vocabulary types are extension seams, not implementations.
