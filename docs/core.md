# Core Primitives

## Overview

Reusable expression machinery in `quantsmind.core`: named math objects,
variables, parameters, composable expressions, formulas, equations, and
an engine that parses and evaluates them.

## Purpose

Give every layer above a shared way to name values, compose expressions
from terms, and evaluate them against variable assignments.

## Concept

`Variable`/`Parameter` hold named values; `Expression` combines terms
with operators and evaluates via keyword assignments (`expr.evaluate(x=2)`);
`Formula` names an expression; `Equation` pairs two expressions with
solution checking; `ExpressionEngine` parses strings like `"x + 1"`.

`MathObject` is the abstract base (name + metadata + `evaluate`).

## API

`Variable`, `Parameter`, `Expression`, `Formula`, `Equation`,
`ExpressionEngine`, `MathObject`.

## Input / Processing / Output

Input: names, terms, assignment keywords. Processing: tree evaluation.
Output: floats and booleans (`check_solution`).

## Example

```python
from quantsmind.core import Equation, Expression, ExpressionEngine

engine = ExpressionEngine()
expr = engine.parse_expression("x + 1")
assert engine.evaluate(expr, x=2) == 3.0
equation = Equation("eq", expr, Expression("const", [4]))
assert equation.check_solution(x=3) is True
```

## Limitations

String parsing covers basic arithmetic only; no symbolic algebra —
see `quantsmind.algebra` and `quantsmind.calculus` for heavier math.
