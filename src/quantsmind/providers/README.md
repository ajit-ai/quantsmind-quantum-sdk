# Providers Package

## Purpose
Defines the vendor-independent contract that hardware, cloud, and simulator backends must implement to plug into QuantsMind.

## Responsibility
Own Provider/Backend interfaces, capability negotiation, and credential/config contracts, without depending on any specific vendor SDK.

## Dependencies
- `quantsmind.core`
- `quantsmind.runtime`
- `quantsmind.exceptions`

## Future Interfaces
- Provider capability discovery protocol
- Backend health-check and quota interfaces
- First-party and third-party provider plugin contracts

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/providers`, `tests/integration/providers`
(placeholders only, no test logic yet).
