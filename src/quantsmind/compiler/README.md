# Compiler Package

## Purpose
Defines the intermediate representation (IR) and transformation pipeline contracts used to lower domain-level descriptions (e.g. quantum circuits, optimization graphs) into backend-executable form.

## Responsibility
Own IR node contracts, pass/transform interfaces, and the pipeline contract that providers plug into. No compiler logic implemented.

## Dependencies
- `quantsmind.core`
- `quantsmind.foundation`
- `quantsmind.exceptions`

## Future Interfaces
- Multi-level IR (domain IR -> backend IR)
- Pass manager and optimization pass contracts
- Target-specific lowering interfaces

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/compiler`, `tests/integration/compiler`
(placeholders only, no test logic yet).
