# Contributing to QuantsMind SDK

Thank you for considering a contribution. QuantsMind is designed for
decades of evolution, so we favor careful, well-justified changes over
speed.

## Before you start

1. Read `docs/architecture-overview.md` and
   `docs/package-dependency-rules.md`.
2. For anything touching architecture (new packages, new cross-package
   dependencies, new public interfaces), open an issue first and, if
   accepted, add an ADR under `architecture/decisions/`.
3. Check `ROADMAP.md` — implementation work should map to a roadmap
   item; if it doesn't, discuss it in an issue first.

## Engineering principles (non-negotiable)

1. Mathematics before implementation.
2. Architecture before code.
3. Interfaces before implementations.
4. Composition before inheritance.
5. Simplicity before optimization.
6. Extensibility before specialization.
7. Documentation before release.
8. Testing before optimization.
9. Vendor independence.
10. Scientific correctness.
11. Clean public APIs.
12. Minimal coupling / high cohesion.
13. Backward compatibility whenever possible.

## Workflow

1. Fork and branch: `feature/<short-desc>`, `fix/<short-desc>`, or
   `docs/<short-desc>`.
2. Make one logical change per PR.
3. Run locally:
   ```bash
   ruff check .
   mypy src
   pytest tests/unit
   ```
4. Update `CHANGELOG.md` under `[Unreleased]`.
5. Open a PR describing *why*, not just *what*.

## New package checklist

- [ ] `src/quantsmind/<name>/__init__.py`
- [ ] `src/quantsmind/<name>/README.md` (Purpose / Responsibility /
      Dependencies / Future Interfaces / Status / Testing)
- [ ] Entry added to `docs/package-dependency-rules.md`
- [ ] Mirrored `tests/unit/<name>`, `tests/integration/<name>`
- [ ] No new circular dependencies

## Code of Conduct

By participating, you agree to abide by `CODE_OF_CONDUCT.md`.

## Reporting security issues

Do not open a public issue. See `SECURITY.md`.
