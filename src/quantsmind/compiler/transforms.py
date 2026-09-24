"""Evaluation and transformation passes over the AST.

The evaluator resolves names against an environment mapping; the
constant-folding pass shrinks trees without changing their meaning.
Both are total over well-formed trees: unknown names and division by
zero raise typed errors instead of returning sentinels.
"""

from __future__ import annotations

from quantsmind.compiler.ast_nodes import BinOp, Name, Node, Number, UnaryOp

__all__ = [
    "EvaluationError",
    "evaluate",
    "fold_constants",
]


class EvaluationError(ValueError):
    """Raised for unbound names and division by zero."""


def evaluate(node: Node, env: dict[str, float] | None = None) -> float:
    """Evaluate a tree against ``env`` (default: empty).

    Raises:
        EvaluationError: For unbound names or division by zero.
    """
    environment = env or {}
    if isinstance(node, Number):
        return node.value
    if isinstance(node, Name):
        if node.identifier not in environment:
            raise EvaluationError(f"unbound name: {node.identifier!r}")
        return float(environment[node.identifier])
    if isinstance(node, UnaryOp):
        value = evaluate(node.operand, environment)
        return value if node.operator == "+" else -value
    if isinstance(node, BinOp):
        left = evaluate(node.left, environment)
        right = evaluate(node.right, environment)
        if node.operator == "+":
            return left + right
        if node.operator == "-":
            return left - right
        if node.operator == "*":
            return left * right
        if node.operator == "/":
            if right == 0.0:
                raise EvaluationError("division by zero")
            return left / right
        if node.operator == "^":
            return float(left**right)
    raise EvaluationError(f"cannot evaluate node: {node!r}")


def fold_constants(node: Node) -> Node:
    """Fold constant subtrees bottom-up (meaning-preserving)."""
    if isinstance(node, BinOp):
        left, right = fold_constants(node.left), fold_constants(node.right)
        if isinstance(left, Number) and isinstance(right, Number):
            if node.operator == "/" and right.value == 0.0:
                return BinOp(node.operator, left, right)
            return Number(evaluate(BinOp(node.operator, left, right)))
        return BinOp(node.operator, left, right)
    if isinstance(node, UnaryOp):
        operand = fold_constants(node.operand)
        if isinstance(operand, Number):
            return Number(operand.value if node.operator == "+" else -operand.value)
        return UnaryOp(node.operator, operand)
    return node
