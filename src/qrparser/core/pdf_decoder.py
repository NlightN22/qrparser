# pdf_decoder.py
# Stateless PDF→image→barcode pipeline using pypdfium2 + zxing-cpp.
# English-only comments inside source.

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import numpy as np
import pypdfium2 as pdfium
from PIL import Image  # noqa: F401  # Pillow is used indirectly via pdfium's .to_pil()
import zxingcpp  # Python bindings for zxing-cpp


@dataclass(frozen=True)
class DecodeSettings:
    """Tunable, immutable decode parameters."""
    scale: float = 3.5
    fallback_scale: float = 5.0


class PdfBarcodeDecoder:
    """Decode QR/DataMatrix/etc barcodes from a PDF file."""

    def __init__(self, settings: DecodeSettings | None = None) -> None:
        self.settings = settings or DecodeSettings()

    @staticmethod
    def _render_page_rgb(page: pdfium.PdfPage, scale: float) -> np.ndarray:
        """Render a pdfium page to an RGB numpy array."""
        pil = page.render(scale=scale).to_pil()
        return np.array(pil.convert("RGB"))

    @staticmethod
    def _decode_all(img_rgb: np.ndarray) -> List[str]:
        """Run zxing-cpp multi-symbology decode and return non-empty texts."""
        results = zxingcpp.read_barcodes(img_rgb)
        return [r.text for r in results if getattr(r, "text", None)]

    def extract_from_pdf(self, pdf_path: Path | str) -> List[str]:
        """Decode all barcodes from all pages. Returns texts in reading order."""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        pdf = pdfium.PdfDocument(str(pdf_path))
        decoded: list[str] = []

        for i in range(len(pdf)):
            page = pdf[i]
            img = self._render_page_rgb(page, scale=self.settings.scale)
            vals = self._decode_all(img)

            if not vals and self.settings.fallback_scale:
                img2 = self._render_page_rgb(page, scale=self.settings.fallback_scale)
                vals = self._decode_all(img2)

            decoded.extend(vals)

        return decoded


__all__ = ["PdfBarcodeDecoder", "DecodeSettings"]
