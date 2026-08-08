# Coding Standards

- Python 3.13+, fully type-hinted (`from __future__ import annotations`)
- `ruff` for linting and formatting (see `pyproject.toml`)
- `mypy --strict` for type checking
- Prefer `abc.ABC` + `@abstractmethod` for public contracts
- Prefer composition of small Protocols over deep inheritance chains
- No implicit `Any`; justify every explicit `Any` with a comment
- Docstrings: Purpose / Responsibility / Dependencies / Future Interfaces
  for every module-level architectural component
