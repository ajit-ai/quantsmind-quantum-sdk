# Known Limitations

Honest gap list for the current release. See `ROADMAP.md` for where each
item is headed and `CHANGELOG.md` for what already changed.

## Quantum layer

- Quantum and hybrid strategies require the optional MicroQuantum engine
  (`pip install "quantsmind[quantum]"`, tested series
  `microquantum>=0.4,<0.5`). Without it, quantum requests honestly
  degrade to classical execution with recorded fallback — never a
  fabricated quantum result.
- No quantum advantage, speedup, or production-optimization claims.
- Supplied-data only: no live market data, no trading, no investment
  advice, no ML model training.

## Package maturity

- Only `quantum` has a frozen public API (`api_manifest.json`). The
  `physics`, `chemistry`, `biology`, `astronomy`, and `cosmology`
  packages now ship small tested foundations (mechanics, elements,
  sequences, sky calculations, expansion); the `finance` (top level),
  `ai`, `compiler`, `datasets`, and `plugins` packages remain contracts
  or skeletons with varying completeness.
- `knowledge` imports cleanly and its value objects are unit-tested, but
  deeper engine behaviors (reasoning, search, provenance flows) have no
  test coverage yet.

## Quality gates

- Global test coverage is ~35%; the CI gate is scoped to
  `quantsmind.quantum` (>=80%, currently ~89%). Untested skeleton code
  does not block releases.
- `mypy --strict` and `ruff` are CI-gated for `quantsmind.quantum` (plus
  `foundation` for mypy). Elsewhere, pre-existing style debt remains:
  long lines (E501), unused-import triage including intentional
  `__init__` re-exports (F401), legacy `typing.Union` aliases (UP007),
  and argument-naming (N803) that would touch public signatures.
- Type policy: `quantsmind.foundation.enums` is the source of truth; the
  `Literal` aliases in `quantsmind.foundation.types` are wire-format
  legacy kept for backward compatibility (see the note in `types.py`).

## Platform notes

- CI runs Python 3.13; local development has been verified on 3.14.
  `requires-python` is `>=3.13`.
- Timestamps are naive datetimes throughout (`datetime.now(UTC)` with
  tzinfo stripped); there is no timezone-aware handling yet.
