# Logging Package

## Purpose
Defines a vendor-independent logging interface used by every other package instead of importing a logging library directly.

## Responsibility
Own Logger/LogRecord/Handler interface contracts.

## Dependencies
- *(none — leaf package)*

## Future Interfaces
- Structured logging contract
- Correlation-ID propagation interfaces

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/logging`, `tests/integration/logging`
(placeholders only, no test logic yet).
