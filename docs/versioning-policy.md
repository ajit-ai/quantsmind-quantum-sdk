# Versioning Policy

QuantsMind follows Semantic Versioning (SemVer 2.0.0): `MAJOR.MINOR.PATCH`.

- `R0.x.y` (0.x) — pre-1.0, architecture and public API may still shift;
  breaking changes are called out in `CHANGELOG.md` and minor-bumped.
- `1.0.0` will be declared once foundation, core, runtime, compiler,
  providers, and at least one domain package (quantum) have stable,
  implemented, tested public APIs.
- Post-1.0: breaking changes require a MAJOR bump and a deprecation
  cycle of at least one MINOR release with warnings.
