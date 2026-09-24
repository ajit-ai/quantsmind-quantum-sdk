"""Abstract syntax tree nodes for the expression language."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "Node",
    "Number",
    "Name",
    "UnaryOp",
    "BinOp",
    "node_count",
]


class Node:
    """Base class for AST nodes."""


@dataclass(frozen=True)
class Number(Node):
    """Numeric literal."""

    value: float


@dataclass(frozen=True)
class Name(Node):
    """Variable reference."""

    identifier: str


@dataclass(frozen=True)
class UnaryOp(Node):
    """Unary plus/minus."""

    operator: str
    operand: Node


@dataclass(frozen=True)
class BinOp(Node):
    """Binary operation."""

    operator: str
    left: Node
    right: Node


def node_count(node: Node) -> int:
    """Count nodes in a tree (including the root)."""
    if isinstance(node, BinOp):
        return 1 + node_count(node.left) + node_count(node.right)
    if isinstance(node, UnaryOp):
        return 1 + node_count(node.operand)
    return 1


def to_dict(node: Node) -> dict[str, Any]:
    """Serialize a tree to a JSON-safe dictionary."""
    if isinstance(node, Number):
        return {"node": "number", "value": node.value}
    if isinstance(node, Name):
        return {"node": "name", "identifier": node.identifier}
    if isinstance(node, UnaryOp):
        return {"node": "unary", "operator": node.operator, "operand": to_dict(node.operand)}
    if isinstance(node, BinOp):
        return {
            "node": "binary",
            "operator": node.operator,
            "left": to_dict(node.left),
            "right": to_dict(node.right),
        }
    raise TypeError(f"unknown node type: {type(node).__name__}")
