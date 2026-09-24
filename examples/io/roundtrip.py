"""IO round-trips: JSON documents, CSV tables, and line streams.

Feature: readers/writers from ``quantsmind.io``.
Purpose: show deterministic interchange with stdlib only.
Input: a dict, two records, a 3-line text file in tmp.
Processing: write -> read back -> compare.
Output: equality confirmations for all three formats.
Meaning: what you write is what you read, byte discipline included.

Run from the repository root::

    python examples/io/roundtrip.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from quantsmind.io import iter_lines, read_csv, read_json, write_csv, write_json


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_json(root / "doc.json", {"a": [1, 2, 3]})
        print(f"json: {read_json(root / 'doc.json') == {'a': [1, 2, 3]}}")
        write_csv(root / "t.csv", ["name", "age"], [{"name": "a", "age": 1}])
        header, rows = read_csv(root / "t.csv")
        print(f"csv: {header == ['name', 'age'] and rows == [{'name': 'a', 'age': '1'}]}")
        (root / "l.txt").write_text("x\ny\n", encoding="utf-8")
        print(f"lines: {list(iter_lines(root / 'l.txt')) == ['x', 'y']}")


if __name__ == "__main__":
    main()
