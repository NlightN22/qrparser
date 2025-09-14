from pathlib import Path

import pytest

from qrparser.core import PdfBarcodeDecoder, DecodeSettings


TEST_PDF = Path(__file__).parent / "fixtures" / "test2.pdf"


@pytest.mark.skipif(not TEST_PDF.exists(), reason="test2.pdf not found at repo root")
def test_extract_from_pdf_smoke():
    """Smoke test: runs pipeline and asserts it returns a list (possibly empty).

    We don't hardcode expected strings because test2.pdf content may change.
    The goal is to verify the pipeline works end-to-end and doesn't crash.
    """
    dec = PdfBarcodeDecoder(DecodeSettings(scale=3.5, fallback_scale=5.0))
    vals = dec.extract_from_pdf(TEST_PDF)

    assert isinstance(vals, list)
    assert all(isinstance(v, str) for v in vals)
    assert len(vals) == 1
