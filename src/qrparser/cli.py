from pathlib import Path
import argparse

from qrparser.core import PdfBarcodeDecoder, DecodeSettings


def main() -> None:
    ap = argparse.ArgumentParser(prog="qrparser", description="Extract barcodes from PDF")
    ap.add_argument("pdf", type=Path, help="Path to PDF")
    ap.add_argument("--scale", type=float, default=3.5)
    ap.add_argument("--fallback-scale", type=float, default=5.0)
    args = ap.parse_args()

    dec = PdfBarcodeDecoder(DecodeSettings(scale=args.scale, fallback_scale=args.fallback_scale))
    vals = dec.extract_from_pdf(args.pdf)

    if not vals:
        print("[warn] No barcodes detected (try --scale 5.0).")
    else:
        for v in vals:
            print(v)


if __name__ == "__main__":
    main()
