"""Unit tests for quantsmind.security primitives."""

from __future__ import annotations

import pytest

from quantsmind.security import (
    hash_password,
    hmac_sign,
    hmac_verify,
    secure_token,
    sha256_hex,
    verify_password,
)


class TestHashing:
    def test_sha256_known(self) -> None:
        assert sha256_hex(b"abc") == (
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        )

    def test_hmac_roundtrip(self) -> None:
        signature = hmac_sign(b"key", b"message")
        assert hmac_verify(b"key", b"message", signature) is True
        assert hmac_verify(b"key", b"other", signature) is False
        with pytest.raises(ValueError):
            hmac_sign(b"", b"message")

    def test_tokens_unique(self) -> None:
        assert secure_token() != secure_token()
        with pytest.raises(ValueError):
            secure_token(0)


class TestPasswords:
    def test_roundtrip(self) -> None:
        hashed = hash_password("s3cret")
        assert verify_password("s3cret", hashed) is True
        assert verify_password("wrong", hashed) is False
        assert verify_password("s3cret", "garbage") is False

    def test_empty_rejected(self) -> None:
        with pytest.raises(ValueError):
            hash_password("")
