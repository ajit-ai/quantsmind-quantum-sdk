# Biology Foundations

## Overview

Sequence primitives in `quantsmind.biology` (`sequences.py`): DNA/RNA
validation, complement, transcription, standard-code translation, and GC
statistics.

## Purpose

Let users run the central dogma (DNA → RNA → protein) on real sequence
fragments with nothing to install beyond the SDK.

## Concept

Sequences are validated uppercase strings; translation walks codons via
the 64-entry `CODON_TABLE`, stopping before the first stop codon and
ignoring a trailing partial codon.

## API

`validate_dna()`, `validate_rna()`, `complement()`,
`reverse_complement()`, `transcribe()`, `translate_rna()`,
`translate_dna()`, `gc_content()`, `CODON_TABLE`, alphabets.

## Input / Processing / Output

Input: base strings. Processing: validation + mapping.
Output: strings and the GC fraction in [0, 1].

## Example

`python examples/biology/central_dogma.py` transcribes and translates a
24-base fragment into `MAIVMGR`.

## Limitations

Educational scope only: no alignment, no phylogeny, no clinical or
diagnostic use, no production bioinformatics.
