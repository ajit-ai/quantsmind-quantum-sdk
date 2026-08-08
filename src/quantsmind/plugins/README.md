# Plugins Package

## Purpose
Defines the extension mechanism that lets third parties add new domains, providers, or backends to QuantsMind without modifying core.

## Responsibility
Own PluginSpec, PluginRegistry, and lifecycle hook interfaces.

## Dependencies
- `quantsmind.core`

## Future Interfaces
- Entry-point based plugin discovery
- Plugin sandboxing / capability restriction contracts

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/plugins`, `tests/integration/plugins`
(placeholders only, no test logic yet).
