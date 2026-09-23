# Chemistry Foundations

## Overview

Element and composition arithmetic in `quantsmind.chemistry`
(`elements.py`): a curated 29-element table, molar-mass math, a minimal
formula parser, and mole/mass/molarity conversions.

## Purpose

Let users compute with real chemical identity (symbols, masses) in a few
lines of dependency-free Python.

## Concept

Compositions are `{symbol: count}` dicts; masses use IUPAC conventional
atomic masses; conversions follow `n = m/M` and `C = n/V`.

## API

`Element`, `ELEMENTS`, `element()`, `molar_mass()`, `parse_formula()`,
`moles_from_mass()`, `mass_from_moles()`, `molarity()`,
`limiting_reactant()`, `theoretical_yield_moles()`,
`AVOGADRO_CONSTANT`.

## Input / Processing / Output

Input: symbols, flat formulas (`"H2O"`), gram/Liter quantities.
Processing: table lookup and arithmetic. Output: g/mol, mol, mol/L.

## Example

`python examples/chemistry/water.py` parses water, weighs 2 moles, and
mixes a 1.0 mol/L solution.

## Limitations

Flat formulas only (no parentheses, charges, hydrates); curated table,
not a full periodic database; no reactions, dynamics, or quantum
chemistry — those are explicitly out of scope.
