"""Central dogma: DNA -> RNA -> protein for a short gene fragment.

Feature: validation, transcription, translation from ``quantsmind.biology``.
Purpose: show the sequence pipeline on one readable example.
Input: DNA "ATGGCCATTGTAATGGGCCGCTGA".
Processing: validate -> transcribe -> translate; plus GC content.
Output: RNA string, "MAIVMGR" protein, 54.2% GC.
Meaning: the start codon yields M, the TGA stop ends translation.

Run from the repository root::

    python examples/biology/central_dogma.py
"""

from __future__ import annotations

from quantsmind.biology import gc_content, reverse_complement, transcribe, translate_dna

DNA = "ATGGCCATTGTAATGGGCCGCTGA"


def main() -> None:
    rna = transcribe(DNA)
    print(f"DNA:     {DNA}")
    print(f"RNA:     {rna}")
    print(f"protein: {translate_dna(DNA)}")
    print(f"GC:      {gc_content(DNA):.1%}")
    print(f"revcomp: {reverse_complement(DNA)}")


if __name__ == "__main__":
    main()
