"""Unit tests for quantsmind.datasets."""

from __future__ import annotations

import pytest

from quantsmind.datasets import Dataset, Schema, SchemaError, describe_numeric


def _schema() -> Schema:
    return Schema({"name": str, "age": int})


def _dataset() -> Dataset:
    dataset = Dataset(_schema(), name="people")
    dataset.extend(
        [
            {"name": "a", "age": 20},
            {"name": "b", "age": 30},
            {"name": "c", "age": 40},
            {"name": "d", "age": 50},
        ]
    )
    return dataset


class TestSchema:
    def test_invalid_record(self) -> None:
        with pytest.raises(SchemaError):
            _dataset().add({"name": "x"})

    def test_bad_schema(self) -> None:
        with pytest.raises(ValueError):
            Schema({})

    def test_atomic_extend(self) -> None:
        dataset = _dataset()
        with pytest.raises(SchemaError):
            dataset.extend([{"name": "ok", "age": 1}, {"name": "bad"}])
        assert len(dataset) == 4


class TestDataset:
    def test_split_and_batch(self) -> None:
        train, test = _dataset().split(0.5)
        assert len(train) == 2
        assert len(test) == 2
        assert train.name == "people/train"
        batches = _dataset().batch(3)
        assert [len(batch) for batch in batches] == [3, 1]
        with pytest.raises(ValueError):
            _dataset().split(1.5)
        with pytest.raises(ValueError):
            _dataset().batch(0)

    def test_transform_and_column(self) -> None:
        dataset = _dataset()
        older = dataset.transform(lambda r: {**r, "age": r["age"] + 1})
        assert older.column("age") == [21, 31, 41, 51]
        with pytest.raises(KeyError):
            dataset.column("nope")

    def test_describe(self) -> None:
        stats = _dataset().describe("age")
        assert stats["count"] == 4.0
        assert stats["mean"] == 35.0
        assert stats["min"] == 20.0
        assert stats["max"] == 50.0

    def test_roundtrip(self) -> None:
        dataset = _dataset()
        rebuilt = Dataset.from_dict(dataset.to_dict(), _schema())
        assert len(rebuilt) == 4
        assert rebuilt.column("name") == ["a", "b", "c", "d"]

    def test_describe_numeric(self) -> None:
        assert describe_numeric([1.0, 2.0, 3.0])["std"] == 0.816496580927726
        with pytest.raises(ValueError):
            describe_numeric([])
