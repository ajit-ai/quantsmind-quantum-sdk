# Finance Package

## Purpose
Defines the domain model for quantitative finance (instruments, portfolios, risk, pricing), building on math, optimization, and AI.

## Responsibility
Own finance domain interfaces. No pricing/risk algorithms implemented.

## Dependencies
- `quantsmind.math`
- `quantsmind.optimization`
- `quantsmind.ai`

## Future Interfaces
- Market data provider contracts
- Portfolio and risk-model interfaces

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/finance`, `tests/integration/finance`
(placeholders only, no test logic yet).
