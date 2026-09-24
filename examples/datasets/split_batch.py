"""Dataset workflow: validate, split, batch, and describe.

Feature: schema-validated `Dataset` from ``quantsmind.datasets``.
Purpose: show the full local data-prep loop with no dependencies.
Input: 10 synthetic age records.
Processing: validate -> 70/30 split -> batches of 4 -> age stats.
Output: split sizes, batch count, mean age 33.5.
Meaning: deterministic prep primitives compose without surprises.

Run from the repository root::

    python examples/datasets/split_batch.py
"""

from __future__ import annotations

from quantsmind.datasets import Dataset, Schema


def main() -> None:
    schema = Schema({"name": str, "age": int})
    dataset = Dataset(schema, name="people")
    dataset.extend([{"name": f"p{i}", "age": 20 + i * 3} for i in range(10)])
    train, test = dataset.split(0.7)
    print(f"train/test: {len(train)}/{len(test)}")
    batches = train.batch(4)
    print(f"batches: {len(batches)} of sizes {[len(b) for b in batches]}")
    stats = dataset.describe("age")
    print(f"mean age: {stats['mean']}")


if __name__ == "__main__":
    main()
