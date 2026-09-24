"""IO Package — Defines file/stream/network IO contracts.

This package is part of the QuantsMind SDK (R0.1.0).
Foundational implementation (Phase 11): JSON/CSV interchange and
streaming readers on the standard library, plus SDK-object boundaries.
"""

from __future__ import annotations

from quantsmind.io.csv_io import CsvError, read_csv, write_csv
from quantsmind.io.json_io import JsonError, dump_object, load_object, read_json, write_json
from quantsmind.io.streams import iter_chunks, iter_lines

__all__: list[str] = [
    "CsvError",
    "read_csv",
    "write_csv",
    "JsonError",
    "read_json",
    "write_json",
    "dump_object",
    "load_object",
    "iter_chunks",
    "iter_lines",
]
