"""Lexical tokens for the expression language.

Tokenizes arithmetic expressions over numbers, names, operators, and
parentheses. Whitespace is insignificant; anything else is a lexical
error with its position.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "Token",
    "TokenKind",
    "LexError",
    "tokenize",
]

#: Token categories.
TokenKind = str

NUMBER = "number"
NAME = "name"
OPERATOR = "operator"
LPAREN = "lparen"
RPAREN = "rparen"
EOF = "eof"

_OPERATORS = frozenset("+-*/^=,;")


class LexError(ValueError):
    """Raised for characters that cannot start a token."""

    def __init__(self, message: str, position: int) -> None:
        """Initialize with a message and source position."""
        super().__init__(f"{message} at position {position}")
        self.position = position


@dataclass(frozen=True)
class Token:
    """One lexical token with its source position.

    Args:
        kind: Token category.
        value: Literal text (numbers keep their spelling).
        position: Offset into the source string.
        metadata: Free-form extra fields.
    """

    kind: TokenKind
    value: str
    position: int
    metadata: dict[str, Any] = field(default_factory=dict)


def tokenize(source: str) -> list[Token]:
    """Split ``source`` into tokens plus a trailing EOF token.

    Raises:
        LexError: For unexpected characters.
    """
    tokens: list[Token] = []
    index = 0
    while index < len(source):
        char = source[index]
        if char.isspace():
            index += 1
        elif char.isdigit() or (
            char == "." and index + 1 < len(source) and source[index + 1].isdigit()
        ):
            start = index
            while index < len(source) and (source[index].isdigit() or source[index] == "."):
                index += 1
            tokens.append(Token(NUMBER, source[start:index], start))
        elif char.isalpha() or char == "_":
            start = index
            while index < len(source) and (source[index].isalnum() or source[index] == "_"):
                index += 1
            tokens.append(Token(NAME, source[start:index], start))
        elif char in _OPERATORS:
            tokens.append(Token(OPERATOR, char, index))
            index += 1
        elif char == "(":
            tokens.append(Token(LPAREN, char, index))
            index += 1
        elif char == ")":
            tokens.append(Token(RPAREN, char, index))
            index += 1
        else:
            raise LexError(f"unexpected character {char!r}", index)
    tokens.append(Token(EOF, "", len(source)))
    return tokens
