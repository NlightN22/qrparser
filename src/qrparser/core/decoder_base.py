# src/qrparser/core/decoder_base.py
from __future__ import annotations
from pathlib import Path
from typing import Protocol, Iterable

class BarcodeDecoder(Protocol):
    def can_handle(self, mime: str) -> bool: ...
    def extract_from_file(self, path: Path) -> Iterable[str]: ...