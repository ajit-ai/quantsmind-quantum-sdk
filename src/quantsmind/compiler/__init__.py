"""Compiler Package — Defines the compiler pipeline contracts.

This package is part of the QuantsMind SDK (R0.1.0).
Foundational implementation (Phase 11): lexing, parsing, AST, and
constant-folding passes for the SDK expression language, plus tree
evaluation. Deliberately an expression front-end, not a language.
"""

from __future__ import annotations

from quantsmind.compiler.ast_nodes import BinOp, Name, Node, Number, UnaryOp, node_count, to_dict
from quantsmind.compiler.parser import ParseError, Parser, parse
from quantsmind.compiler.tokens import LexError, Token, tokenize
from quantsmind.compiler.transforms import EvaluationError, evaluate, fold_constants

__all__: list[str] = [
    "BinOp",
    "Name",
    "Node",
    "Number",
    "UnaryOp",
    "node_count",
    "to_dict",
    "ParseError",
    "Parser",
    "parse",
    "LexError",
    "Token",
    "tokenize",
    "EvaluationError",
    "evaluate",
    "fold_constants",
]
