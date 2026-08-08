# Cosmology Package

## Purpose
Defines the domain model for large-scale universe structure and evolution, building on astronomy and physics.

## Responsibility
Own cosmology domain interfaces. No cosmology algorithms implemented.

## Dependencies
- `quantsmind.astronomy`
- `quantsmind.physics`

## Future Interfaces
- Cosmological model parameter contracts
- Large-scale structure simulation interfaces

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/cosmology`, `tests/integration/cosmology`
(placeholders only, no test logic yet).
