"""Biological sequence foundations.

DNA/RNA representation with validation, complement and reverse-complement
operations, transcription (DNA -> RNA), translation (RNA -> protein via
the standard genetic code), and GC-content statistics. Deterministic and
dependency-free; educational scope only.
"""

from __future__ import annotations

__all__ = [
    "DNA_ALPHABET",
    "RNA_ALPHABET",
    "CODON_TABLE",
    "validate_dna",
    "validate_rna",
    "complement",
    "reverse_complement",
    "transcribe",
    "translate_rna",
    "translate_dna",
    "gc_content",
    "hamming_distance",
    "point_mutation",
]

#: Valid DNA bases.
DNA_ALPHABET = frozenset("ATGC")
#: Valid RNA bases.
RNA_ALPHABET = frozenset("AUGC")

#: Standard genetic code: RNA codon -> amino acid (``*`` = stop).
CODON_TABLE: dict[str, str] = {
    "UUU": "F", "UUC": "F", "UUA": "L", "UUG": "L",
    "UCU": "S", "UCC": "S", "UCA": "S", "UCG": "S",
    "UAU": "Y", "UAC": "Y", "UAA": "*", "UAG": "*",
    "UGU": "C", "UGC": "C", "UGA": "*", "UGG": "W",
    "CUU": "L", "CUC": "L", "CUA": "L", "CUG": "L",
    "CCU": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "CAU": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "CGU": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "AUU": "I", "AUC": "I", "AUA": "I", "AUG": "M",
    "ACU": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "AAU": "N", "AAC": "N", "AAA": "K", "AAG": "K",
    "AGU": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GUU": "V", "GUC": "V", "GUA": "V", "GUG": "V",
    "GCU": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "GAU": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "GGU": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}

_DNA_COMPLEMENT = {"A": "T", "T": "A", "G": "C", "C": "G"}


def validate_dna(sequence: str) -> str:
    """Validate a DNA sequence (uppercased) and return it.

    Raises:
        ValueError: For empty sequences or invalid bases.
    """
    sequence = sequence.upper()
    if not sequence:
        raise ValueError("DNA sequence must not be empty")
    invalid = sorted(set(sequence) - DNA_ALPHABET)
    if invalid:
        raise ValueError(f"invalid DNA bases: {invalid}")
    return sequence


def validate_rna(sequence: str) -> str:
    """Validate an RNA sequence (uppercased) and return it.

    Raises:
        ValueError: For empty sequences or invalid bases.
    """
    sequence = sequence.upper()
    if not sequence:
        raise ValueError("RNA sequence must not be empty")
    invalid = sorted(set(sequence) - RNA_ALPHABET)
    if invalid:
        raise ValueError(f"invalid RNA bases: {invalid}")
    return sequence


def complement(sequence: str) -> str:
    """DNA complement (A<->T, G<->C)."""
    sequence = validate_dna(sequence)
    return "".join(_DNA_COMPLEMENT[base] for base in sequence)


def reverse_complement(sequence: str) -> str:
    """Reverse complement of a DNA sequence."""
    return complement(sequence)[::-1]


def transcribe(dna: str) -> str:
    """Transcribe DNA to RNA (T -> U)."""
    return validate_dna(dna).replace("T", "U")


def translate_rna(rna: str) -> str:
    """Translate RNA to a protein string, stopping before the first stop codon.

    Trailing incomplete codons are ignored.

    Raises:
        ValueError: For invalid RNA bases.
    """
    rna = validate_rna(rna)
    protein: list[str] = []
    for index in range(0, len(rna) - 2, 3):
        amino = CODON_TABLE[rna[index : index + 3]]
        if amino == "*":
            break
        protein.append(amino)
    return "".join(protein)


def translate_dna(dna: str) -> str:
    """Transcribe then translate a DNA sequence."""
    return translate_rna(transcribe(dna))


def gc_content(sequence: str) -> float:
    """GC fraction of a DNA sequence, in ``[0, 1]``."""
    sequence = validate_dna(sequence)
    gc = sum(1 for base in sequence if base in {"G", "C"})
    return gc / len(sequence)


def hamming_distance(first: str, second: str) -> int:
    """Number of differing positions between two equal-length DNA sequences.

    Raises:
        ValueError: For invalid bases or unequal lengths.
    """
    first, second = validate_dna(first), validate_dna(second)
    if len(first) != len(second):
        raise ValueError(
            f"sequences must have equal length, got {len(first)} vs {len(second)}"
        )
    return sum(1 for a, b in zip(first, second, strict=True) if a != b)


def point_mutation(sequence: str, index: int, base: str) -> str:
    """Return a copy of a DNA sequence with one base replaced.

    Raises:
        ValueError: For invalid sequences, out-of-range indices, or
            invalid replacement bases.
    """
    sequence = validate_dna(sequence)
    base = base.upper()
    if base not in DNA_ALPHABET:
        raise ValueError(f"invalid DNA base: {base!r}")
    if not 0 <= index < len(sequence):
        raise ValueError(f"index {index!r} out of range for length {len(sequence)}")
    return sequence[:index] + base + sequence[index + 1 :]
