# IO Foundations

## Overview

Interchange helpers in `quantsmind.io`: JSON documents, CSV tables, and
streaming readers on the standard library, plus SDK-object boundaries
for anything exposing `to_dict` / `from_dict`.

## Purpose

Let users persist and reload SDK data deterministically with explicit,
typed errors instead of bare I/O exceptions.

## Concept

`read_json`/`write_json` for documents, `read_csv`/`write_csv` for
header-checked tables, `iter_lines`/`iter_chunks` for bounded streams;
`dump_object`/`load_object` bridge SDK objects; `JsonError`/`CsvError`
wrap every failure mode.

## API

`read_json()`, `write_json()`, `dump_object()`, `load_object()`,
`read_csv()`, `write_csv()`, `iter_lines()`, `iter_chunks()`,
`JsonError`, `CsvError`.

## Input / Processing / Output

Input: paths and JSON-safe data. Processing: UTF-8 encode/decode with
validation. Output: restored documents, tables, streams.

## Example

`python examples/io/roundtrip.py` round-trips all three formats through
a temporary directory.

## Limitations

Local filesystem only; no network transports, no Parquet/Arrow, no
schema evolution — boundaries are explicit, not magical.
