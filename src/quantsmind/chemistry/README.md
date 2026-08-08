# Chemistry Package

## Purpose
Defines the domain model for molecular and chemical systems, building on the physics domain for atomic-scale interactions.

## Responsibility
Own chemistry domain interfaces (molecules, reactions, bonds). No chemistry algorithms implemented.

## Dependencies
- `quantsmind.physics`
- `quantsmind.math`

## Future Interfaces
- Molecular representation interoperability (SMILES, etc.)
- Reaction network contracts

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/chemistry`, `tests/integration/chemistry`
(placeholders only, no test logic yet).
