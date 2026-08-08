# Exceptions Package

## Purpose
Defines the SDK-wide exception hierarchy so every package raises consistent, catchable, well-documented errors.

## Responsibility
Own the base QuantsMindError hierarchy and domain-error taxonomy.

## Dependencies
- *(none — leaf package)*

## Future Interfaces
- Domain-specific exception subclasses per package
- Error code / diagnostic metadata contracts

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/exceptions`, `tests/integration/exceptions`
(placeholders only, no test logic yet).
