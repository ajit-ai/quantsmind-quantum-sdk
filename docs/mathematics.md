# Mathematics Foundations

## Overview

Reusable mathematics across `quantsmind.math`, `algebra`, `calculus`,
`numerical`, `statistics`, `optimization`, and `ml_math`: vectors and
matrices, polynomials, differentiation, root finding, distributions,
gradient optimizers, and loss functions. Pure Python, no dependencies.

## Purpose

Give science and domain layers one tested numerical vocabulary instead
of scattered reimplementations.

## Concept

Value objects (`CoordinateVector`, `DenseMatrix`, `Polynomial`,
distributions) plus stateless functions (distances, losses) and stateful
solvers/optimizers with histories.

## API

See each package: `math.linear_algebra`, `math.numerical`,
`algebra.Polynomial`, `calculus.Differentiator`,
`statistics.NormalDistribution`/`PoissonDistribution`,
`optimization.AdamOptimizer`, `ml_math.MSELoss`.

## Input / Processing / Output

Input: vectors, matrices, coefficients, callables. Processing: exact or
finite-difference numerics. Output: floats, vectors, histories.

## Examples

`examples/math/linear_algebra.py`,
`examples/calculus/differentiation.py`,
`examples/statistics/distributions.py`,
`examples/optimization/adam_descent.py`.

## Limitations

No batched/accelerated kernels (see the pairwise batch helper in the
quantum data layer for the pattern); single-threaded iterative methods;
`math/*` vs top-level mirrors are historical — both work, consolidation
is a future decision, not this page.
