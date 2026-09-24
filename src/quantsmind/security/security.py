"""Carefully scoped security primitives (standard library only).

Hashing (SHA-256), HMAC signing/verification with constant-time
comparison, password hashing via PBKDF2-HMAC-SHA256, and secure token
generation. No custom cryptography: every primitive delegates to
:mod:`hashlib`, :mod:`hmac`, or :mod:`secrets`.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

__all__ = [
    "sha256_hex",
    "hmac_sign",
    "hmac_verify",
    "secure_token",
    "hash_password",
    "verify_password",
]


def sha256_hex(data: bytes) -> str:
    """SHA-256 hex digest of ``data``."""
    return hashlib.sha256(data).hexdigest()


def hmac_sign(key: bytes, message: bytes) -> str:
    """HMAC-SHA256 hex signature (keys must be non-empty)."""
    if not key:
        raise ValueError("HMAC key must not be empty")
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def hmac_verify(key: bytes, message: bytes, signature: str) -> bool:
    """Verify an HMAC signature with a constant-time comparison."""
    expected = hmac_sign(key, message)
    return hmac.compare_digest(expected, signature)


def secure_token(num_bytes: int = 32) -> str:
    """Cryptographically secure URL-safe token.

    Raises:
        ValueError: If ``num_bytes`` is not positive.
    """
    if num_bytes <= 0:
        raise ValueError(f"num_bytes must be positive, got {num_bytes!r}")
    return secrets.token_urlsafe(num_bytes)


def hash_password(password: str, *, salt: bytes | None = None, iterations: int = 600_000) -> str:
    """PBKDF2-HMAC-SHA256 password hash as ``iterations$salt$digest``.

    Raises:
        ValueError: For empty passwords or bogus parameters.
    """
    if not password:
        raise ValueError("password must not be empty")
    if iterations < 1:
        raise ValueError(f"iterations must be positive, got {iterations!r}")
    raw_salt = salt if salt is not None else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), raw_salt, iterations)
    return f"{iterations}${raw_salt.hex()}${digest.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against :func:`hash_password` output."""
    try:
        iterations_str, salt_hex, _ = hashed.split("$")
        candidate = hash_password(
            password, salt=bytes.fromhex(salt_hex), iterations=int(iterations_str)
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(candidate, hashed)
