from pathlib import Path
import time, uuid, pathlib, argparse

from qrparser.core import PdfBarcodeDecoder, DecodeSettings

from qrparser.observability.logging import (
    setup_logging, get_logger, set_request_context,
    log_request_start, log_request_end,
)


def main() -> None:
    setup_logging()
    logger = get_logger(__name__)
    ap = argparse.ArgumentParser(prog="qrparser", description="Extract barcodes from PDF")
    ap.add_argument("pdf", type=Path, help="Path to PDF")
    ap.add_argument("--scale", type=float, default=3.5)
    ap.add_argument("--fallback-scale", type=float, default=5.0)
    args = ap.parse_args()

    set_request_context(request_id=str(uuid.uuid4()))
    t0 = time.perf_counter()
    log_request_start(method="CLI", path=str(args.pdf), scale=args.scale, fallback_scale=args.fallback_scale)

    try:
        from qrparser.core.pdf_decoder import PdfBarcodeDecoder, DecodeSettings
        dec = PdfBarcodeDecoder(DecodeSettings(scale=args.scale, fallback_scale=args.fallback_scale))
        values = dec.decode(args.pdf)
        dur = (time.perf_counter() - t0) * 1000
        log_request_end(status=0, duration_ms=dur, found=len(values))
        for v in values:
            print(v)
    except Exception:
        logger.exception("Unhandled error during CLI decode")
        raise


if __name__ == "__main__":
    main()
