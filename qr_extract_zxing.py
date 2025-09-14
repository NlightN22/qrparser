# qr_extract_zxing.py
# Detect QR/DataMatrix/etc from PDF pages using zxing-cpp (no external DLLs).
# Comments in English only.

from pathlib import Path
import argparse
import numpy as np
from PIL import Image
import pypdfium2 as pdfium
import zxingcpp  # module name for zxing-cpp Python bindings

def render_page_rgb(page, scale: float = 3.0) -> np.ndarray:
    """Render PDF page with pdfium and return an RGB numpy array."""
    pil = page.render(scale=scale).to_pil()
    return np.array(pil.convert("RGB"))

def decode_all(img_rgb: np.ndarray) -> list[str]:
    """Run zxing-cpp multi-symbology decode and return non-empty texts."""
    results = zxingcpp.read_barcodes(img_rgb)
    # Filter out empties; preserve order of detection
    return [r.text for r in results if r.text]

def extract_from_pdf(pdf_path: Path, scale: float = 3.5) -> list[str]:
    pdf = pdfium.PdfDocument(str(pdf_path))
    decoded: list[str] = []
    for i in range(len(pdf)):
        page = pdf[i]
        img = render_page_rgb(page, scale=scale)
        vals = decode_all(img)
        # Fallback: oversample a bit more if nothing found on this page
        if not vals:
            img2 = render_page_rgb(page, scale=5.0)
            vals = decode_all(img2)
        decoded.extend(vals)
    return decoded

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--scale", type=float, default=3.5, help="Initial render scale (try 3.0–5.0)")
    args = ap.parse_args()
    vals = extract_from_pdf(args.pdf, scale=args.scale)
    if not vals:
        print("[warn] No barcodes detected (try --scale 5.0).")
    else:
        for v in vals:
            print(v)

if __name__ == "__main__":
    main()
