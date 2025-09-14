# comments in English only
from __future__ import annotations
import os
import qrparser.config.settings as conf


def _clean_env(monkeypatch):
    # wipe all QR_* variables to ensure a clean slate
    for k in [k for k in os.environ.keys() if k.startswith("QR_")]:
        monkeypatch.delenv(k, raising=False)
    conf.reset_settings_cache()


def test_defaults_are_applied(monkeypatch):
    _clean_env(monkeypatch)
    s = conf.get_settings()

    assert s.APP_NAME == "qrparser"
    assert s.LOG_LEVEL == "INFO"
    assert s.DECODE_SCALE == 3.0
    assert s.HTTP_PORT == 8000

    # New fields: accept PDF + PNG/JPEG by default
    assert s.ALLOWED_MIME_PDF == ("application/pdf",)
    assert s.ALLOWED_MIME_IMG == ("image/png", "image/jpeg")
    assert s.ALL_ALLOWED_MIME == ("application/pdf", "image/png", "image/jpeg")


def test_env_overrides(monkeypatch):
    _clean_env(monkeypatch)
    monkeypatch.setenv("QR_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("QR_HTTP_PORT", "9000")

    # Complex types must be JSON
    # Keep PDFs default and narrow images to only PNG for the test:
    monkeypatch.setenv("QR_ALLOWED_MIME_IMG", '["image/png"]')

    conf.reset_settings_cache()
    s = conf.get_settings()

    assert s.LOG_LEVEL == "DEBUG"
    assert s.HTTP_PORT == 9000
    assert s.ALLOWED_MIME_IMG == ("image/png",)
    # Combined view reflects the override
    assert s.ALL_ALLOWED_MIME == ("application/pdf", "image/png")


def test_types_and_bounds(monkeypatch):
    _clean_env(monkeypatch)
    # wrong key is ignored (double prefix)
    monkeypatch.setenv("QR_QR_DECODE_SCALE", "10.0")
    # correct key wins
    monkeypatch.setenv("QR_DECODE_SCALE", "4.5")
    # wrong key ignored
    monkeypatch.setenv("QR_QR_MAX_PAGES", "10")
    # correct key wins
    monkeypatch.setenv("QR_MAX_PAGES", "10")

    conf.reset_settings_cache()
    s = conf.get_settings()

    assert s.DECODE_SCALE == 4.5
    assert s.MAX_PAGES == 10
