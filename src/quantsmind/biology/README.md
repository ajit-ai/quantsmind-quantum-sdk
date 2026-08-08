# Biology Package

## Purpose
Defines the domain model for biological systems (molecules to populations), building on chemistry for molecular-scale interactions.

## Responsibility
Own biology domain interfaces. No biology algorithms implemented.

## Dependencies
- `quantsmind.chemistry`
- `quantsmind.math`

## Future Interfaces
- Sequence and structure representation contracts
- Population and evolutionary dynamics interfaces

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/biology`, `tests/integration/biology`
(placeholders only, no test logic yet).
