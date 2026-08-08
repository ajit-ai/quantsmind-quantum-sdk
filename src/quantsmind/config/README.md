# Configuration Package

## Purpose
Defines contracts for loading, validating, and resolving SDK and application configuration from multiple sources.

## Responsibility
Own Config, ConfigSource, and Schema interfaces.

## Dependencies
- `quantsmind.utils`

## Future Interfaces
- Layered config resolution (env, file, remote) contracts
- Schema validation interfaces

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/config`, `tests/integration/config`
(placeholders only, no test logic yet).
