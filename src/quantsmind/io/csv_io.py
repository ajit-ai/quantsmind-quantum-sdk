"""CSV interchange helpers (standard library only).

Row-oriented reading/writing for ``list[dict[str, str]]`` records with
explicit headers and strict column checks.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

__all__ = [
    "CsvError",
    "read_csv",
    "write_csv",
]


class CsvError(OSError):
    """Raised when CSV reading or writing fails."""


def read_csv(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    """Read a CSV file with a header row.

    Returns:
        ``(header, rows)`` where every row maps each header to a string.

    Raises:
        CsvError: If the file cannot be read or has no header.
    """
    try:
        text = Path(path).read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise CsvError(f"cannot read CSV from {path}: {exc}") from exc
    lines = text.splitlines()
    if not lines:
        raise CsvError(f"CSV file is empty: {path}")
    reader = csv.DictReader(lines)
    header = list(reader.fieldnames or [])
    rows = [
        {key: (value if value is not None else "") for key, value in row.items()}
        for row in reader
    ]
    return header, rows


def write_csv(path: str | Path, header: list[str], rows: list[dict[str, Any]]) -> None:
    """Write records under ``header`` (extra keys rejected).

    Raises:
        CsvError: For empty headers, unknown keys, or write failures.
    """
    if not header:
        raise CsvError("CSV header must not be empty")
    for index, row in enumerate(rows):
        unknown = sorted(set(row) - set(header))
        if unknown:
            raise CsvError(f"row {index} has unknown columns: {unknown}")
    try:
        with open(path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=header, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({key: row.get(key, "") for key in header})
    except OSError as exc:
        raise CsvError(f"cannot write CSV to {path}: {exc}") from exc
