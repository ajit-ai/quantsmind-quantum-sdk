# Security Package

## Purpose
Defines contracts for authentication, authorization, secrets, and cryptographic operations used by providers and I/O.

## Responsibility
Own Credential, AuthProvider, and SecretStore interfaces.

## Dependencies
- `quantsmind.utils`
- `quantsmind.exceptions`

## Future Interfaces
- Pluggable secret backend contracts (vaults, env, files)
- Provider credential negotiation interfaces

## Status
Architecture-only (R0.1.0). No scientific, numerical, or algorithmic
implementations exist in this package yet. All classes are interfaces,
abstract base classes, or empty skeletons documenting intended shape.

## Testing
See `tests/unit/security`, `tests/integration/security`
(placeholders only, no test logic yet).
