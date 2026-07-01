"""Read/write helpers for Genshin UGC GI file container format."""

from __future__ import annotations

import struct
from pathlib import Path

from miliastra_agent.core.models import GiFileHeader

HEAD_MAGIC = 0x0326
TAIL_MAGIC = 0x0679

GI_TYPE_GIP = 1
GI_TYPE_GIL = 2
GI_TYPE_GIA = 3
GI_TYPE_GIR = 4


def read_header(data: bytes) -> GiFileHeader:
    if len(data) < 20:
        raise ValueError("File too short for GI header")

    file_size, version, head_magic, file_type, content_length = struct.unpack(">5I", data[:20])
    if head_magic != HEAD_MAGIC:
        raise ValueError(f"Invalid head magic: {head_magic:#x}, expected {HEAD_MAGIC:#x}")

    tail_offset = file_size
    if len(data) < tail_offset + 4:
        raise ValueError("File too short for GI tail magic")

    tail_magic = struct.unpack(">I", data[tail_offset : tail_offset + 4])[0]
    if tail_magic != TAIL_MAGIC:
        raise ValueError(f"Invalid tail magic: {tail_magic:#x}, expected {TAIL_MAGIC:#x}")

    return GiFileHeader(
        file_size=file_size,
        version=version,
        head_magic=head_magic,
        file_type=file_type,
        content_length=content_length,
    )


def read_payload(path: Path) -> bytes:
    data = path.read_bytes()
    header = read_header(data)
    start = 20
    end = start + header.content_length
    return data[start:end]


def wrap_payload(payload: bytes, file_type: int, version: int = 1) -> bytes:
    content_length = len(payload)
    file_size = 20 + content_length
    header = struct.pack(">5I", file_size, version, HEAD_MAGIC, file_type, content_length)
    tail = struct.pack(">I", TAIL_MAGIC)
    return header + payload + tail


def write_gia(path: Path, payload: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(wrap_payload(payload, GI_TYPE_GIA))
    return path
