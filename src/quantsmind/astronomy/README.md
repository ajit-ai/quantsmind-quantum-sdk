# Astronomy Package

## Purpose
Defines the domain model for astronomical systems (bodies, orbits, observations), building on physics.

## Responsibility
Own astronomy domain interfaces. No astronomy algorithms implemented.

## Dependencies
- `quantsmind.physics`
- `quantsmind.math`

## Future Interfaces
- Celestial coordinate system contracts
- Observational data ingestion interfaces

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/astronomy`, `tests/integration/astronomy`
(placeholders only, no test logic yet).
