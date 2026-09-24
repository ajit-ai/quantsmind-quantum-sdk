# Datasets Foundations

## Overview

Schema-validated in-memory datasets in `quantsmind.datasets`: records,
schemas, deterministic splitting and batching, transforms, column
statistics, and serialization boundaries.

## Purpose

Let users validate, split, batch, and summarize record data with plain
dicts and no dependencies.

## Concept

A `Schema` declares field types and required names; `Dataset` enforces
it on every write (atomic `extend`), iterates in insertion order, and
derives train/test splits, batches, and numeric summaries.

## API

`Schema`, `Dataset`, `SchemaError`, `describe_numeric()`.

## Input / Processing / Output

Input: dict records. Processing: validation + slicing. Output:
subsets, batches, statistic dicts, JSON-safe dicts.

## Example

`python examples/datasets/split_batch.py` validates 10 records, splits
70/30, batches, and reports mean age 33.5.

## Limitations

In-memory only (no lazy frames, no SQL); single-process; numeric stats
are population-based; no proprietary datasets bundled.
