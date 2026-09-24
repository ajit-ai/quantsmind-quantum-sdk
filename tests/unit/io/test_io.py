"""Unit tests for quantsmind.io."""

from __future__ import annotations

from pathlib import Path

import pytest

from quantsmind.datasets import Dataset, Schema
from quantsmind.io import (
    CsvError,
    JsonError,
    dump_object,
    iter_chunks,
    iter_lines,
    load_object,
    read_csv,
    read_json,
    write_csv,
    write_json,
)


def _schema() -> Schema:
    return Schema({"name": str, "age": int})


class TestJson:
    def test_roundtrip(self, tmp_path: Path) -> None:
        path = tmp_path / "data.json"
        write_json(path, {"a": [1, 2, 3]})
        assert read_json(path) == {"a": [1, 2, 3]}

    def test_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(JsonError):
            read_json(tmp_path / "nope.json")

    def test_sdk_object_boundary(self, tmp_path: Path) -> None:
        dataset = Dataset(_schema(), name="d")
        dataset.add({"name": "a", "age": 1})
        path = tmp_path / "dataset.json"
        dump_object(dataset, path)
        assert read_json(path)["records"] == [{"name": "a", "age": 1}]

    def test_load_object_roundtrip(self, tmp_path: Path) -> None:
        from quantsmind.quantum import QuantumProgram

        path = tmp_path / "program.json"
        dump_object(QuantumProgram.bell_state(), path)
        rebuilt = load_object(QuantumProgram, path)
        assert rebuilt.to_dict() == QuantumProgram.bell_state().to_dict()

    def test_sdk_object_needs_from_dict(self, tmp_path: Path) -> None:
        with pytest.raises(JsonError):
            load_object(int, tmp_path / "dataset.json")


class TestCsv:
    def test_roundtrip(self, tmp_path: Path) -> None:
        path = tmp_path / "data.csv"
        write_csv(path, ["name", "age"], [{"name": "a", "age": 1}])
        header, rows = read_csv(path)
        assert header == ["name", "age"]
        assert rows == [{"name": "a", "age": "1"}]

    def test_unknown_column(self, tmp_path: Path) -> None:
        with pytest.raises(CsvError):
            write_csv(tmp_path / "bad.csv", ["a"], [{"a": "1", "b": "2"}])

    def test_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(CsvError):
            read_csv(tmp_path / "nope.csv")


class TestStreams:
    def test_lines_and_chunks(self, tmp_path: Path) -> None:
        path = tmp_path / "lines.txt"
        path.write_text("a\nb\nc\n", encoding="utf-8")
        assert list(iter_lines(path)) == ["a", "b", "c"]
        assert b"".join(iter_chunks(path, size=2)) == path.read_bytes()

    def test_bad_chunk_size(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError):
            list(iter_chunks(tmp_path / "x", size=0))
