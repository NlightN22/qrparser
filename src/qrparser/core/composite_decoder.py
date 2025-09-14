# src/qrparser/core/composite_decoder.py
from __future__ import annotations
from pathlib import Path
from typing import Iterable, Sequence

class CompositeDecoder:
    def __init__(self, decoders: Sequence) -> None:
        self._decoders = list(decoders)

    def can_handle(self, mime: str) -> bool:
        return any(d.can_handle(mime) for d in self._decoders)

    def extract_from_file(self, path: Path, mime: str) -> Iterable[str]:
        for d in self._decoders:
            if d.can_handle(mime):
                return d.extract_from_file(path)
        raise ValueError(f"No decoder for mime: {mime}")