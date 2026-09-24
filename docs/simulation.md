# Simulation Foundations

## Overview

Generic system-evolution contracts plus a working engine in
`quantsmind.simulation`: register named simulator callables, run them
with parameters, and inspect history.

## Purpose

Let users orchestrate deterministic model runs without any framework.

## Concept

`SimulationEngine` maps names to callables; `run_simulation` records
every run; `Experiment` carries run metadata.

## API

`SimulationEngine`, `Simulator`, `SimulationResult`, `Experiment`.

## Input / Processing / Output

Input: simulator name + parameter dict. Processing: direct callable
dispatch. Output: result object plus history entries.

## Example

`python examples/simulation/engine_demo.py` registers a doubler,
runs it over 21, and shows one history entry.

## Limitations

In-process callables only; no distributed execution, no quantum
simulation (that lives in MicroQuantum — never duplicated here).
