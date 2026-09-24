"""JSON interchange helpers (standard library only).

Read/write JSON documents plus SDK-object boundaries for anything
exposing ``to_dict`` / ``from_dict``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

__all__ = [
    "JsonError",
    "read_json",
    "write_json",
    "dump_object",
    "load_object",
]


class JsonError(OSError):
    """Raised when JSON reading, writing, or decoding fails."""


def read_json(path: str | Path) -> Any:
    """Read and decode a JSON document.

    Raises:
        JsonError: If the file cannot be read or decoded.
    """
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise JsonError(f"cannot read JSON from {path}: {exc}") from exc


def write_json(path: str | Path, data: Any, *, indent: int = 2) -> None:
    """Encode ``data`` as JSON and write it (UTF-8).

    Raises:
        JsonError: If the data is not encodable or writing fails.
    """
    try:
        Path(path).write_text(json.dumps(data, indent=indent) + "\n", encoding="utf-8")
    except (OSError, TypeError, ValueError) as exc:
        raise JsonError(f"cannot write JSON to {path}: {exc}") from exc


def dump_object(obj: Any, path: str | Path) -> None:
    """Write an SDK object exposing ``to_dict()`` as JSON.

    Raises:
        JsonError: If the object has no ``to_dict`` or writing fails.
    """
    to_dict = getattr(obj, "to_dict", None)
    if not callable(to_dict):
        raise JsonError(f"object {type(obj).__name__!r} has no to_dict() method")
    write_json(path, to_dict())


def load_object(cls: type, path: str | Path) -> Any:
    """Read JSON and rebuild via ``cls.from_dict(data)``.

    Raises:
        JsonError: If reading fails or ``from_dict`` is missing/broken.
    """
    from_dict = getattr(cls, "from_dict", None)
    if not callable(from_dict):
        raise JsonError(f"class {getattr(cls, '__name__', cls)!r} has no from_dict() method")
    try:
        return from_dict(read_json(path))
    except JsonError:
        raise
    except Exception as exc:
        name = getattr(cls, "__name__", cls)
        raise JsonError(f"cannot rebuild {name!r} from {path}: {exc}") from exc
