"""Lightweight, safe symbolic expressions for QUBO/Ising formulation.

QMQ-02 introduces a small expression model sufficient to **represent** and
**evaluate** the quadratic polynomials used by objectives, constraints,
penalties and QUBO/Ising forms.  It supports constants, variables, addition,
subtraction, multiplication and integer powers.

This is deliberately **not** a symbolic algebra system: there is no
simplification engine, no differentiation and no transcendental functions.
The value is reliable representation and evaluation without ``eval()``.

The canonical expansion :meth:`Expression.expand` reduces an expression to a
dict of monomials `((variable, ...) -> coefficient)` with sorted keys and a
constant entry in the empty tuple.  A product of two occurrences of ``x``
produces the monomial ``("x", "x")`` so binary idempotence (``x^2 = x``) can
be applied by a later QUBO phase — it is not applied here.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, ClassVar

_VARIABLE_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class ExpressionError(ValueError):
    """Base error for symbolic expression problems."""


class ExpressionParseError(ExpressionError):
    """Raised when an expression string cannot be parsed."""


@dataclass(frozen=True)
class Expression:
    """Base class of the symbolic expression tree.

    Subclasses are immutable.  Operator overloads construct new nodes, so
    ``2 * x + 1`` written against the returned ``Expression`` objects stays
    symbolic and never evaluates eagerly.
    """

    def evaluate(self, assignments: dict[str, Any]) -> float:
        """Numerically evaluate the expression against variable assignments."""
        raise NotImplementedError

    @property
    def variables(self) -> tuple[str, ...]:
        """Variable names referenced by this expression (order of appearance)."""
        raise NotImplementedError

    def expand(self) -> dict[tuple[str, ...], float]:
        """Expand into a canonical monomial map.

        Keys are single variable names (linear) or tuples of variable names
        (products, duplicates preserved, sorted).  The constant term is keyed
        by the empty tuple ``()``.
        """
        raise NotImplementedError

    # -- operator overloads ---------------------------------------------

    def __add__(self, other: object) -> Sum:
        return Sum((self, coerce_expression(other)))

    def __radd__(self, other: object) -> Sum:
        return Sum((coerce_expression(other), self))

    def __sub__(self, other: object) -> Sum:
        return Sum((self, Scale(-1.0, coerce_expression(other))))

    def __rsub__(self, other: object) -> Sum:
        return Sum((coerce_expression(other), Scale(-1.0, self)))

    def __mul__(self, other: object) -> Product:
        return Product((self, coerce_expression(other)))

    def __rmul__(self, other: object) -> Product:
        return Product((coerce_expression(other), self))

    def __neg__(self) -> Scale:
        return Scale(-1.0, self)

    def __repr__(self) -> str:
        return str(self)


@dataclass(frozen=True)
class Constant(Expression):
    """A literal numeric constant."""

    value: float
    kind: ClassVar[str] = "constant"

    def __post_init__(self) -> None:
        if not math.isfinite(self.value):
            raise ExpressionError(f"constant must be finite, got {self.value!r}")

    def evaluate(self, assignments: dict[str, Any]) -> float:
        return float(self.value)

    @property
    def variables(self) -> tuple[str, ...]:
        return ()

    def expand(self) -> dict[tuple[str, ...], float]:
        return {(): float(self.value)} if self.value != 0.0 else {}

    def __str__(self) -> str:
        if self.value == int(self.value):
            return str(int(self.value))
        return str(self.value)


@dataclass(frozen=True)
class VariableExpression(Expression):
    """A reference to a decision variable."""

    name: str
    kind: ClassVar[str] = "variable"

    def __post_init__(self) -> None:
        if not _VARIABLE_PATTERN.fullmatch(self.name):
            raise ExpressionError(f"invalid variable name {self.name!r}; expected an identifier")

    def evaluate(self, assignments: dict[str, Any]) -> float:
        try:
            value = assignments[self.name]
        except KeyError:
            raise KeyError(f"expression references missing variable {self.name!r}") from None
        return float(value)

    @property
    def variables(self) -> tuple[str, ...]:
        return (self.name,)

    def expand(self) -> dict[tuple[str, ...], float]:
        return {(self.name,): 1.0}

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Scale(Expression):
    """A scalar multiple of an expression."""

    coefficient: float
    expression: Expression
    kind: ClassVar[str] = "scale"

    def __post_init__(self) -> None:
        if not math.isfinite(self.coefficient):
            raise ExpressionError(f"coefficient must be finite, got {self.coefficient!r}")

    def evaluate(self, assignments: dict[str, Any]) -> float:
        return self.coefficient * self.expression.evaluate(assignments)

    @property
    def variables(self) -> tuple[str, ...]:
        return self.expression.variables

    def expand(self) -> dict[tuple[str, ...], float]:
        return {
            monomial: coefficient * self.coefficient
            for monomial, coefficient in self.expression.expand().items()
            if coefficient != 0.0
        }

    def __str__(self) -> str:
        return f"{self.coefficient}*({self.expression})"


@dataclass(frozen=True)
class Sum(Expression):
    """A sum of expressions (nested sums are flattened)."""

    terms: tuple[Expression, ...]
    kind: ClassVar[str] = "sum"

    def __post_init__(self) -> None:
        object.__setattr__(self, "terms", _flatten_sum(self.terms))

    def evaluate(self, assignments: dict[str, Any]) -> float:
        return sum(term.evaluate(assignments) for term in self.terms)

    @property
    def variables(self) -> tuple[str, ...]:
        seen: list[str] = []
        for term in self.terms:
            for name in term.variables:
                if name not in seen:
                    seen.append(name)
        return tuple(seen)

    def expand(self) -> dict[tuple[str, ...], float]:
        result: dict[tuple[str, ...], float] = {}
        for term in self.terms:
            for monomial, coefficient in term.expand().items():
                result[monomial] = result.get(monomial, 0.0) + coefficient
        return {m: c for m, c in result.items() if c != 0.0}

    def __str__(self) -> str:
        return " + ".join(str(term) for term in self.terms)


@dataclass(frozen=True)
class Product(Expression):
    """A product of expressions."""

    factors: tuple[Expression, ...]
    kind: ClassVar[str] = "product"

    def __post_init__(self) -> None:
        object.__setattr__(self, "factors", _flatten_product(self.factors))

    def evaluate(self, assignments: dict[str, Any]) -> float:
        value = 1.0
        for factor in self.factors:
            value *= factor.evaluate(assignments)
        return value

    @property
    def variables(self) -> tuple[str, ...]:
        seen: list[str] = []
        for factor in self.factors:
            for name in factor.variables:
                if name not in seen:
                    seen.append(name)
        return tuple(seen)

    def expand(self) -> dict[tuple[str, ...], float]:
        result: dict[tuple[str, ...], float] = {(): 1.0}
        for factor in self.factors:
            factor_map = factor.expand()
            combined: dict[tuple[str, ...], float] = {}
            for left, left_coefficient in result.items():
                for right, right_coefficient in factor_map.items():
                    key = tuple(sorted(left + right))
                    combined[key] = combined.get(key, 0.0) + left_coefficient * right_coefficient
            result = {k: v for k, v in combined.items() if v != 0.0}
        return result

    def __str__(self) -> str:
        return "*".join(str(factor) for factor in self.factors)


def _flatten_sum(terms: tuple[Expression, ...]) -> tuple[Expression, ...]:
    flattened: list[Expression] = []
    for term in terms:
        if isinstance(term, Sum):
            flattened.extend(term.terms)
        else:
            flattened.append(term)
    return tuple(flattened)


def _flatten_product(factors: tuple[Expression, ...]) -> tuple[Expression, ...]:
    flattened: list[Expression] = []
    for factor in factors:
        if isinstance(factor, Product):
            flattened.extend(factor.factors)
        else:
            flattened.append(factor)
    return tuple(flattened)


# ---------------------------------------------------------------------------
# construction helpers
# ---------------------------------------------------------------------------


def var(name: str) -> VariableExpression:
    """Build a :class:`VariableExpression` for ``name``."""
    return VariableExpression(name)


def const(value: float) -> Constant:
    """Build a :class:`Constant` from a numeric value."""
    return Constant(float(value))


def coefficient(value: float, expression: Expression) -> Scale:
    """Build a scalar multiple ``value * expression``."""
    return Scale(float(value), expression)


def coerce_expression(value: Any) -> Expression:
    """Coerce a number, string or Expression into an Expression.

    Raises:
        ExpressionError: If ``value`` is a callable or an unsupported type.
            Callables cannot be introspected into monomials, so automatic
            QUBO/penalty formulation requires symbolic strings or nodes.
    """
    if isinstance(value, Expression):
        return value
    if isinstance(value, bool):
        value = int(value)
    if isinstance(value, (int, float)):
        return Constant(float(value))
    if isinstance(value, str):
        return parse_expression(value)
    if callable(value):
        raise ExpressionError(
            "cannot coerce a callable expression into a symbolic form; "
            "automatic QUBO/penalty formulation requires a symbolic string "
            "or Expression"
        )
    raise ExpressionError(
        "cannot coerce expression of type "
        f"{type(value).__name__}; use a symbolic string or Expression"
    )


def parse_expression(text: str) -> Expression:
    """Parse a safe arithmetic expression string into an Expression tree.

    Supported grammar: numbers, identifiers, ``+ - * ( )``, unary minus and
    integer powers via ``**`` or ``^``.  No ``eval()`` is used anywhere.

    Raises:
        ExpressionParseError: If the text is not a valid expression.
    """
    tokens = _tokenize(text)
    parser = _Parser(tokens)
    expression = parser.parse_additive()
    if parser.current is not None:
        raise ExpressionParseError(f"unexpected trailing token {parser.current!r}")
    return expression


def evaluate_expression(value: Any, assignments: dict[str, Any]) -> float:
    """Evaluate a number, string, Expression or callable.

    Callables are called directly (this is the only path that executes user
    code); everything else goes through the safe symbolic evaluator.
    """
    if callable(value) and not isinstance(value, Expression):
        return float(value(assignments))
    return float(coerce_expression(value).evaluate(assignments))


# ---------------------------------------------------------------------------
# tokenizer / parser
# ---------------------------------------------------------------------------

_NUMBER_TOKEN = re.compile(r"\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?")


def _is_number(token: str) -> bool:
    return bool(_NUMBER_TOKEN.fullmatch(token))


def _tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if char in "+-()^":
            tokens.append(char)
            index += 1
            continue
        if char == "*":
            if index + 1 < length and text[index + 1] == "*":
                tokens.append("**")
                index += 2
            else:
                tokens.append("*")
                index += 1
            continue
        match = _NUMBER_TOKEN.match(text, index)
        if match is not None:
            tokens.append(match.group(0))
            index = match.end()
            continue
        if char.isalpha() or char == "_":
            start = index
            index += 1
            while index < length and (text[index].isalnum() or text[index] == "_"):
                index += 1
            tokens.append(text[start:index])
            continue
        raise ExpressionParseError(f"unexpected character {char!r} in expression")
    return tokens


class _Parser:
    def __init__(self, tokens: list[str]) -> None:
        self.tokens = tokens
        self.position = 0

    @property
    def current(self) -> str | None:
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def _take(self) -> str:
        token = self.tokens[self.position]
        self.position += 1
        return token

    def parse_additive(self) -> Expression:
        expression = self.parse_multiplicative()
        while self.current in {"+", "-"}:
            operator = self._take()
            right = self.parse_multiplicative()
            expression = expression + right if operator == "+" else expression - right
        return expression

    def parse_multiplicative(self) -> Expression:
        expression = self.parse_unary()
        while self.current == "*":
            self._take()
            expression = expression * self.parse_unary()
        return expression

    def parse_power(self) -> Expression:
        base = self.parse_atom()
        if self.current not in {"**", "^"}:
            return base
        self._take()
        token = self.current
        if token is None or not _is_number(token):
            raise ExpressionParseError("expected an integer exponent")
        self._take()
        try:
            exponent = int(float(token))
        except ValueError:
            raise ExpressionParseError(f"exponent must be an integer, got {token!r}") from None
        if float(token) != exponent:
            raise ExpressionParseError(f"exponent must be an integer, got {token!r}")
        if exponent < 0:
            raise ExpressionParseError("exponent must be >= 0")
        if exponent > 32:
            raise ExpressionParseError("exponent too large (max 32)")
        if exponent == 0:
            return Constant(1.0)
        result: Expression = base
        for _ in range(1, exponent):
            result = result * base
        return result

    def parse_unary(self) -> Expression:
        if self.current == "-":
            self._take()
            return -self.parse_unary()
        return self.parse_power()

    def parse_atom(self) -> Expression:
        token = self.current
        if token is None:
            raise ExpressionParseError("unexpected end of expression")
        if token == "(":
            self._take()
            expression = self.parse_additive()
            if self.current != ")":
                raise ExpressionParseError("missing closing ')'")
            self._take()
            return expression
        if _is_number(token):
            self._take()
            return Constant(float(token))
        if _VARIABLE_PATTERN.fullmatch(token):
            self._take()
            return VariableExpression(token)
        raise ExpressionParseError(f"unexpected token {token!r}")


__all__ = [
    "Expression",
    "ExpressionError",
    "ExpressionParseError",
    "Constant",
    "VariableExpression",
    "Scale",
    "Sum",
    "Product",
    "var",
    "const",
    "coefficient",
    "coerce_expression",
    "parse_expression",
    "evaluate_expression",
]
