# src/qrparser/core/image_decoder.py
# comments in English only
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np
from PIL import Image, ImageOps
import zxingcpp  # Python bindings for zxing-cpp


@dataclass(frozen=True)
class DecodeSettings:
    """Tunable, immutable decode parameters for image decoding."""
    scale: float = 3.5
    fallback_scale: float = 5.0


class ImageBarcodeDecoder:
    """
    Decode QR/DataMatrix/etc barcodes from raster images.
    Single-frame only (PNG, JPEG, optional BMP). Stateless.
    """

    SUPPORTED = {
        "image/png",
        "image/jpeg",
        # uncomment if you really need it (usually fine)
        # "image/bmp",
    }

    def __init__(self, settings: DecodeSettings | None = None) -> None:
        self.settings = settings or DecodeSettings()

    def can_handle(self, mime: str) -> bool:
        return mime in self.SUPPORTED

    @staticmethod
    def _pil_to_rgb_np(img: Image.Image) -> np.ndarray:
        """Convert PIL image to RGB numpy array."""
        return np.array(img.convert("RGB"), copy=False)

    @staticmethod
    def _resize(img: Image.Image, factor: float) -> Image.Image:
        """Resize PIL image by a scale factor using a high-quality filter."""
        if factor == 1.0:
            return img
        w, h = img.size
        nw, nh = max(1, int(round(w * factor))), max(1, int(round(h * factor)))
        return img.resize((nw, nh), resample=Image.BICUBIC)

    @staticmethod
    def _decode_all(img_rgb: np.ndarray) -> List[str]:
        """Run zxing-cpp and return non-empty texts."""
        results = zxingcpp.read_barcodes(img_rgb)
        return [r.text for r in results if getattr(r, "text", None)]

    def extract_from_file(self, img_path: Path | str) -> List[str]:
        """
        Decode all barcodes from a single-frame image. Returns texts.
        """
        p = Path(img_path)
        if not p.exists():
            raise FileNotFoundError(f"Image not found: {p}")

        with Image.open(str(p)) as im:
            # Apply EXIF orientation if present (common for JPEGs from phones)
            im = ImageOps.exif_transpose(im)
            im.load()  # ensure loaded before resizing/convert

            # Primary try
            primary = self._resize(im, self.settings.scale)
            vals = self._decode_all(self._pil_to_rgb_np(primary))
            if vals:
                return vals

            # Fallback try
            if self.settings.fallback_scale and self.settings.fallback_scale != self.settings.scale:
                fb = self._resize(im, self.settings.fallback_scale)
                vals = self._decode_all(self._pil_to_rgb_np(fb))

            return vals
