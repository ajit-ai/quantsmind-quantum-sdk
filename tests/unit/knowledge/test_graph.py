"""Unit tests for the knowledge graph value behavior."""

from __future__ import annotations

from quantsmind.knowledge.graph.knowledge_graph import KnowledgeGraph


class TestKnowledgeGraph:
    def test_nodes_edges_paths(self) -> None:
        graph = KnowledgeGraph("g1")
        graph.add_node("a")
        graph.add_node("b")
        graph.add_edge("a", "b")
        assert set(graph.nodes) == {"a", "b"}
        assert graph.neighbors("a") == ["b"]
        assert graph.shortest_path("a", "b") == ["a", "b"]
        assert graph.degree("a") == 1

    def test_remove(self) -> None:
        graph = KnowledgeGraph("g1")
        graph.add_node("a")
        graph.add_node("b")
        graph.add_edge("a", "b")
        assert graph.remove_edge("a", "b") is True
        assert graph.neighbors("a") == []
        assert graph.remove_node("b") is True
        assert set(graph.nodes) == {"a"}
