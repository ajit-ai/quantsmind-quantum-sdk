"""Unit tests for quantsmind.logging capture."""

from __future__ import annotations

import logging

from quantsmind.logging import MemoryHandler, get_logger


class TestCapture:
    def test_context_propagates(self) -> None:
        logger = logging.getLogger("qm-test-capture")
        handler = MemoryHandler()
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        try:
            get_logger("qm-test-capture", {"request": "r1"}).info("hello")
            get_logger("qm-test-capture").bind(job="j2").warning("careful")
        finally:
            logger.removeHandler(handler)
        assert [(r.level, r.message) for r in handler.records] == [
            ("INFO", "hello"),
            ("WARNING", "careful"),
        ]
        assert handler.records[0].context == {"request": "r1"}
        assert handler.records[1].context == {"job": "j2"}
        handler.clear()
        assert handler.records == []

    def test_names(self) -> None:
        assert get_logger("qm-test-name").name == "qm-test-name"
