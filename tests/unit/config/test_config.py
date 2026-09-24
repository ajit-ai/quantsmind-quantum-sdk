"""Unit tests for quantsmind.config layering."""

from __future__ import annotations

import pytest

from quantsmind.config import Config, ConfigError


def _config(monkeypatch: pytest.MonkeyPatch) -> Config:
    monkeypatch.delenv("QM_SERVER_PORT", raising=False)
    return Config(
        defaults={"server": {"host": "localhost", "port": 80}},
        schema={"server": {"host": str, "port": int}},
    )


class TestPrecedence:
    def test_override_wins(self, monkeypatch: pytest.MonkeyPatch) -> None:
        config = _config(monkeypatch)
        config.set("server", "port", 8080)
        assert config.get("server", "port") == 8080

    def test_env_casting(self, monkeypatch: pytest.MonkeyPatch) -> None:
        config = _config(monkeypatch)
        monkeypatch.setenv("QM_SERVER_PORT", "9000")
        assert config.get("server", "port") == 9000

    def test_defaults_and_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        config = _config(monkeypatch)
        assert config.get("server", "host") == "localhost"
        assert config.get("server", "missing") is None

    def test_bad_env_cast(self, monkeypatch: pytest.MonkeyPatch) -> None:
        config = _config(monkeypatch)
        monkeypatch.setenv("QM_SERVER_PORT", "not-a-port")
        try:
            config.get("server", "port")
        except ConfigError:
            return
        raise AssertionError("expected ConfigError")


class TestValidation:
    def test_schema_violation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        config = _config(monkeypatch)
        config.set("server", "port", "fast")
        assert config.validate() != []
        assert Config({"server": {}}).validate() == []

    def test_to_dict(self, monkeypatch: pytest.MonkeyPatch) -> None:
        config = _config(monkeypatch)
        config.set("server", "port", 8080)
        assert config.to_dict()["server"]["port"] == 8080
