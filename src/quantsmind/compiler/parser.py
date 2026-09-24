"""Recursive-descent parser for the expression language.

Grammar (lowest to highest precedence)::

    expression := term (("+" | "-") term)*
    term       := factor (("*" | "/") factor)*
    factor     := unary ("^" unary)?        # right associative
    unary      := ("+" | "-") unary | primary
    primary    := NUMBER | NAME | "(" expression ")"

Division by zero and unbound names surface at evaluation, not parse,
time; syntax problems raise :class:`ParseError` with positions.
"""

from __future__ import annotations

from quantsmind.compiler.ast_nodes import BinOp, Name, Node, Number, UnaryOp
from quantsmind.compiler.tokens import EOF, LPAREN, NAME, NUMBER, OPERATOR, RPAREN, Token, tokenize

__all__ = [
    "ParseError",
    "Parser",
    "parse",
]


class ParseError(ValueError):
    """Raised for syntactically invalid input."""

    def __init__(self, message: str, position: int) -> None:
        """Initialize with a message and source position."""
        super().__init__(f"{message} at position {position}")
        self.position = position


class Parser:
    """Parses a token stream into an AST.

    Args:
        tokens: Token list (without the trailing EOF is fine).
    """

    def __init__(self, tokens: list[Token]) -> None:
        """Initialize over a token list."""
        self._tokens = [token for token in tokens if token.kind != EOF]
        self._position = 0

    def parse(self) -> Node:
        """Parse one expression; trailing tokens are an error.

        Raises:
            ParseError: On empty input, bad syntax, or trailing tokens.
        """
        if not self._tokens:
            raise ParseError("empty expression", 0)
        node = self._parse_expression()
        if self._position != len(self._tokens):
            raise ParseError(
                f"unexpected trailing {self._tokens[self._position].value!r}",
                self._tokens[self._position].position,
            )
        return node

    def _peek(self) -> Token | None:
        if self._position < len(self._tokens):
            return self._tokens[self._position]
        return None

    def _advance(self) -> Token:
        token = self._tokens[self._position]
        self._position += 1
        return token

    def _parse_expression(self) -> Node:
        node = self._parse_term()
        while (token := self._peek()) is not None and self._is_operator(token, {"+", "-"}):
            self._advance()
            node = BinOp(token.value, node, self._parse_term())
        return node

    def _parse_term(self) -> Node:
        node = self._parse_factor()
        while (token := self._peek()) is not None and self._is_operator(token, {"*", "/"}):
            self._advance()
            node = BinOp(token.value, node, self._parse_factor())
        return node

    @staticmethod
    def _is_operator(token: Token, values: set[str]) -> bool:
        """Check whether a token is one of the given operators."""
        return token.kind == OPERATOR and token.value in values

    def _parse_factor(self) -> Node:
        node = self._parse_unary()
        token = self._peek()
        if token is not None and token.kind == OPERATOR and token.value == "^":
            self._advance()
            node = BinOp("^", node, self._parse_factor())
        return node

    def _parse_unary(self) -> Node:
        token = self._peek()
        if token is not None and token.kind == OPERATOR and token.value in {"+", "-"}:
            self._advance()
            return UnaryOp(token.value, self._parse_unary())
        return self._parse_primary()

    def _parse_primary(self) -> Node:
        token = self._peek()
        if token is None:
            raise ParseError("unexpected end of expression", -1)
        if token.kind == NUMBER:
            self._advance()
            return Number(float(token.value))
        if token.kind == NAME:
            self._advance()
            return Name(token.value)
        if token.kind == LPAREN:
            self._advance()
            node = self._parse_expression()
            closing = self._peek()
            if closing is None or closing.kind != RPAREN:
                raise ParseError("missing closing parenthesis", token.position)
            self._advance()
            return node
        raise ParseError(f"unexpected {token.value!r}", token.position)


def parse(source: str) -> Node:
    """Tokenize and parse ``source`` into an AST.

    Raises:
        LexError: For invalid characters.
        ParseError: For invalid syntax.
    """
    return Parser(tokenize(source)).parse()
