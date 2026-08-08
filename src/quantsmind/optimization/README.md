# Optimization Package

## Purpose
Defines contracts for expressing and solving optimization problems (objectives, constraints, solvers) used across finance, AI, physics, and quantum domains.

## Responsibility
Own Objective, Constraint, Solver, and OptimizationResult interfaces. No optimization algorithms implemented.

## Dependencies
- `quantsmind.math`
- `quantsmind.foundation`
- `quantsmind.exceptions`

## Future Interfaces
- Convex / non-convex problem classification contracts
- Gradient and gradient-free solver interfaces
- Multi-objective and constrained optimization contracts

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/optimization`, `tests/integration/optimization`
(placeholders only, no test logic yet).
