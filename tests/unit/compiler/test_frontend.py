"""Unit tests for the compiler expression front-end."""

from __future__ import annotations

import pytest

from quantsmind.compiler import (
    EvaluationError,
    LexError,
    ParseError,
    evaluate,
    fold_constants,
    node_count,
    parse,
    to_dict,
    tokenize,
)


class TestLexer:
    def test_tokens(self) -> None:
        tokens = tokenize("x + 12.5")
        assert [(t.kind, t.value) for t in tokens[:3]] == [
            ("name", "x"),
            ("operator", "+"),
            ("number", "12.5"),
        ]
        assert tokens[-1].kind == "eof"

    def test_bad_character(self) -> None:
        with pytest.raises(LexError):
            tokenize("x @ y")


class TestParser:
    def test_precedence(self) -> None:
        tree = parse("2 + 3 * 4")
        assert evaluate(tree) == 14.0

    def test_parens_and_power(self) -> None:
        assert evaluate(parse("(2 + 3) * 4")) == 20.0
        assert evaluate(parse("2 ^ 3 ^ 2")) == 512.0

    def test_unary(self) -> None:
        assert evaluate(parse("-x"), {"x": 5.0}) == -5.0

    def test_trailing_tokens(self) -> None:
        with pytest.raises(ParseError):
            parse("1 2")

    def test_unbalanced(self) -> None:
        with pytest.raises(ParseError):
            parse("(1 + 2")


class TestEvaluation:
    def test_unbound_name(self) -> None:
        with pytest.raises(EvaluationError):
            evaluate(parse("x + 1"), {})

    def test_division_by_zero(self) -> None:
        with pytest.raises(EvaluationError):
            evaluate(parse("1 / 0"))


class TestTransforms:
    def test_fold_shrinks(self) -> None:
        tree = parse("2 + 3 * 4")
        folded = fold_constants(tree)
        assert node_count(folded) == 1
        assert evaluate(folded) == 14.0

    def test_fold_preserves_meaning(self) -> None:
        tree = parse("2 + 3 * x")
        folded = fold_constants(tree)
        assert evaluate(folded, {"x": 4.0}) == evaluate(tree, {"x": 4.0}) == 14.0

    def test_serialization(self) -> None:
        assert to_dict(parse("1 + x"))["node"] == "binary"
