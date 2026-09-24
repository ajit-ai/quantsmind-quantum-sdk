# Compiler Foundations

## Overview

An expression front-end in `quantsmind.compiler`: lexer, recursive-descent
parser, AST nodes, constant folding, and tree evaluation. Deliberately a
front-end for arithmetic expressions — not a programming language.

## Purpose

Let users tokenize, parse, transform, and evaluate SDK expressions with
positioned diagnostics, independent of any backend.

## Concept

`tokenize()` yields `Token`s; `Parser`/`parse()` builds `Number`,
`Name`, `UnaryOp`, `BinOp` trees; `fold_constants()` shrinks constant
subtrees; `evaluate()` resolves names against an environment dict.
`LexError`, `ParseError`, and `EvaluationError` carry positions.

## API

`tokenize()`, `Token`, `LexError`, `parse()`, `Parser`, `ParseError`,
`Number`, `Name`, `UnaryOp`, `BinOp`, `node_count()`, `to_dict()`,
`evaluate()`, `fold_constants()`, `EvaluationError`.

## Input / Processing / Output

Input: expression strings. Processing: lex → parse → fold → eval.
Output: values, smaller trees, JSON-safe dicts.

## Example

`python examples/compiler/expr_eval.py` runs `"2 + 3 * x"` end to end.

## Limitations

Arithmetic only (no functions, no assignment); no bytecode or machine
targets; division by zero and unbound names are runtime errors by
design.
