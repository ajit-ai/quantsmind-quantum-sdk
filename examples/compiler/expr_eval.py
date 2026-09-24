"""Expression front-end: tokenize, parse, fold, and evaluate.

Feature: lexer/parser/AST from ``quantsmind.compiler``.
Purpose: show the full front-end pipeline on one expression.
Input: the string "2 + 3 * x" with x = 4.
Processing: tokenize -> parse -> constant-fold -> evaluate.
Output: 5 tokens, folded tree of 5 nodes, value 14.0.
Meaning: each stage is inspectable; folding preserves meaning.

Run from the repository root::

    python examples/compiler/expr_eval.py
"""

from __future__ import annotations

from quantsmind.compiler import evaluate, fold_constants, node_count, parse, tokenize


def main() -> None:
    source = "2 + 3 * x"
    tokens = tokenize(source)
    print(f"tokens: {len(tokens) - 1}")  # minus trailing EOF
    tree = parse(source)
    folded = fold_constants(tree)
    print(f"nodes: {node_count(tree)} -> {node_count(folded)}")
    env = {"x": 4.0}
    print(f"value: {evaluate(tree, env)} == {evaluate(folded, env)}")


if __name__ == "__main__":
    main()
