# Developer Guide

## Getting started

```bash
git clone <repo-url>
cd quantsmind-sdk
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Repository layout

See `architecture-overview.md` for the layering model and
`package-dependency-rules.md` for what may depend on what.

## Adding a new package

1. Create `src/quantsmind/<name>/__init__.py` and `README.md`.
2. Document Purpose, Responsibility, Dependencies, Future Interfaces.
3. Add mirrored directories under `tests/unit/<name>`,
   `tests/integration/<name>`.
4. Update `docs/package-dependency-rules.md`.
5. Open a PR following `CONTRIBUTING.md`.

## Running checks locally

```bash
ruff check .
mypy src
pytest tests/unit
```
