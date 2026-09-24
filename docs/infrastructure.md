# Infrastructure Foundations

## Overview

The SDK base in five small packages: layered `config`, contextual
`logging`, explicit `plugins`, stdlib-only `security` primitives, and
local-first `telemetry`. Shared errors root at `QuantsMindError`, and
`utils` holds only genuinely reusable helpers.

## Purpose

Let applications bootstrap configuration, observability, extensions,
and integrity checks with no dependencies and no hidden behavior.

## Concept

`Config` resolves defaults < environment < overrides with schema
casting. `SDKLogger` binds context fields over the standard library;
`MemoryHandler` captures records for tests. `PluginRegistry`
registers/enables/disables with compatibility checks — discovery is an
explicit opt-in, never automatic. `security` wraps hashlib/hmac/secrets
only. `Collector` records events, counters, gauges, and spans
in-process; nothing transmits.

## API

`Config`, `ConfigError`, `SDKLogger`, `get_logger`, `MemoryHandler`,
`LogRecord`, `Plugin`, `PluginMetadata`, `PluginRegistry`,
`PluginError`, `IncompatiblePluginError`, `sha256_hex()`,
`hmac_sign()`, `hmac_verify()`, `secure_token()`, `hash_password()`,
`verify_password()`, `Collector`, `Counter`, `Gauge`, `Span`,
`TelemetryEvent`, `QuantsMindError`, plus the `utils` helpers.

## Input / Processing / Output

Input: dicts, env vars, passwords, callables. Processing: validation
and delegation. Output: resolved values, records, verdicts, digests.

## Example

`python examples/infrastructure/sdk_base.py` resolves a port, captures
a log line, enables a plugin, records an event, and hashes an id.

## Limitations

No remote config stores, no log shippers, no plugin marketplace, no
custom cryptography, no telemetry transport — sinks and backends are
the application's job.
