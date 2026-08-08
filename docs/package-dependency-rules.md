# Package Dependency Rules

## Layers (lower -> higher)

1. `exceptions`, `utils`, `logging` — no internal dependencies
2. `config`, `io`, `security` — depend only on layer 1
3. `foundation` — depends only on `exceptions`
4. `core` — depends on `foundation`, `exceptions`
5. `math` — depends on `foundation`, `exceptions`
6. `runtime`, `compiler`, `providers` — depend on `core`, `foundation`, `exceptions`
7. `optimization` — depends on `math`, `foundation`, `exceptions`
8. `simulation` — depends on `foundation`, `core`, `math`
9. Domain packages: `quantum` (+runtime/compiler/providers), `physics`,
   `chemistry` (-> physics), `biology` (-> chemistry), `astronomy` (->
   physics), `cosmology` (-> astronomy, physics), `ai`, `finance` (->
   math, optimization, ai)
10. `visualization`, `datasets`, `plugins`, `telemetry` — depend on
    lower layers only, never on domain packages

## Hard rules

- No circular imports between packages, ever.
- Domain packages never import each other except via the explicit
  arrows above (e.g. `chemistry -> physics` is allowed; `physics ->
  chemistry` is not).
- Only `providers` may reference vendor-specific SDKs, and only behind
  optional extras in `pyproject.toml`.
