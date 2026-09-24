"""Streaming readers (standard library only).

Memory-bounded line/chunk iteration for large text files.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

__all__ = [
    "iter_lines",
    "iter_chunks",
]


def iter_lines(path: str | Path, *, keepends: bool = False) -> Iterator[str]:
    """Yield text lines one at a time (UTF-8).

    Raises:
        OSError: If the file cannot be opened.
    """
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            yield line if keepends else line.rstrip("\n").rstrip("\r")


def iter_chunks(path: str | Path, size: int = 8192) -> Iterator[bytes]:
    """Yield raw byte chunks of ``size`` from a file.

    Raises:
        ValueError: If size is not positive.
        OSError: If the file cannot be opened.
    """
    if size <= 0:
        raise ValueError(f"chunk size must be positive, got {size!r}")
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(size)
            if not chunk:
                break
            yield chunk
