"""Unit tests for quantsmind.biology.sequences."""

from __future__ import annotations

import pytest

from quantsmind.biology import (
    complement,
    gc_content,
    hamming_distance,
    point_mutation,
    reverse_complement,
    transcribe,
    translate_dna,
    translate_rna,
)


class TestDnaOperations:
    def test_complement(self) -> None:
        assert complement("ATGC") == "TACG"

    def test_reverse_complement(self) -> None:
        assert reverse_complement("ATGC") == "GCAT"

    def test_transcribe(self) -> None:
        assert transcribe("ATGC") == "AUGC"

    def test_gc_content(self) -> None:
        assert gc_content("ATGC") == pytest.approx(0.5)
        assert gc_content("GGCC") == pytest.approx(1.0)

    def test_invalid_base(self) -> None:
        with pytest.raises(ValueError):
            complement("ATGCX")

    def test_empty(self) -> None:
        with pytest.raises(ValueError):
            gc_content("")


class TestTranslation:
    def test_start_and_stop(self) -> None:
        assert translate_rna("AUGGCCUAA") == "MA"

    def test_no_stop_runs_full_length(self) -> None:
        assert translate_rna("AUGGCC") == "MA"

    def test_incomplete_trailing_codon_ignored(self) -> None:
        assert translate_rna("AUGGCCU") == "MA"

    def test_translate_dna(self) -> None:
        assert translate_dna("ATGGCCTAA") == "MA"

    def test_invalid_rna(self) -> None:
        with pytest.raises(ValueError):
            translate_rna("AUGX")


class TestVariation:
    def test_hamming(self) -> None:
        assert hamming_distance("ATGC", "ATGG") == 1
        assert hamming_distance("ATGC", "ATGC") == 0
        with pytest.raises(ValueError):
            hamming_distance("ATG", "ATGC")

    def test_point_mutation(self) -> None:
        assert point_mutation("ATGC", 0, "G") == "GTGC"
        with pytest.raises(ValueError):
            point_mutation("ATGC", 9, "G")
