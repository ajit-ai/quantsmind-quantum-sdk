"""Knowledge graph: model a tiny citation network and traverse it.

Feature: `KnowledgeGraph` from ``quantsmind.knowledge``.
Purpose: show entity/relationship modeling with inspectable traversal.
Input: papers a/b/c with a->b and b->c citations.
Processing: add nodes/edges, query neighbors, paths, degrees.
Output: traversal facts proving the chain structure.
Meaning: relationships are data you can walk, not just store.

Run from the repository root::

    python examples/knowledge/graph_demo.py
"""

from __future__ import annotations

from quantsmind.knowledge.graph.knowledge_graph import KnowledgeGraph


def main() -> None:
    graph = KnowledgeGraph("citations")
    for node in ("a", "b", "c"):
        graph.add_node(node)
    graph.add_edge("a", "b")
    graph.add_edge("b", "c")
    print(f"nodes: {sorted(graph.nodes)}")
    print(f"neighbors of a: {graph.neighbors('a')}")
    print(f"path a->c: {graph.shortest_path('a', 'c')}")
    print(f"degree of b: {graph.degree('b')}")


if __name__ == "__main__":
    main()
