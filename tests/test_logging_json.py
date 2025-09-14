from __future__ import annotations
import json
import logging
import os

from qrparser.observability.logging import setup_logging, get_logger, set_request_context

def test_structlog_json_basic(monkeypatch, capsys):
    monkeypatch.setenv("LOG_FORMAT", "json")
    monkeypatch.setenv("LOG_DEST", "stdout")
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    setup_logging()

    set_request_context(request_id="req-1")
    log = get_logger("qrparser.test")
    log.info("hello", foo=123)

    out = capsys.readouterr().out.strip()
    assert out, "stdout пуст — лог не был перехвачен"
    data = json.loads(out)

    assert data["event"] == "hello"
    assert data["level"] == "info"
    assert data["foo"] == 123
    assert data["request_id"] == "req-1"
    assert "timestamp" in data
