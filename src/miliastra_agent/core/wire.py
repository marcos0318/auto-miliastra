"""Low-level protobuf field iteration helpers."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from google.protobuf.internal import decoder, wire_format


def iter_fields(data: bytes) -> Iterator[tuple[int, int, Any]]:
    """Yield (field_number, wire_type, value) for each field in a protobuf message."""
    pos = 0
    while pos < len(data):
        tag, new_pos = decoder._DecodeVarint(data, pos)
        if new_pos == pos:
            break
        field_number = tag >> 3
        wire_type = tag & 7
        pos = new_pos
        if wire_type == wire_format.WIRETYPE_VARINT:
            value, pos = decoder._DecodeVarint(data, pos)
            yield field_number, wire_type, value
        elif wire_type == wire_format.WIRETYPE_LENGTH_DELIMITED:
            length, pos = decoder._DecodeVarint(data, pos)
            yield field_number, wire_type, data[pos : pos + length]
            pos += length
        elif wire_type == wire_format.WIRETYPE_FIXED32:
            yield field_number, wire_type, data[pos : pos + 4]
            pos += 4
        elif wire_type == wire_format.WIRETYPE_FIXED64:
            yield field_number, wire_type, data[pos : pos + 8]
            pos += 8
        else:
            break


def get_varint(data: bytes, field_number: int) -> int | None:
    for fn, wt, value in iter_fields(data):
        if fn == field_number and wt == wire_format.WIRETYPE_VARINT:
            return int(value)
    return None


def get_string(data: bytes, field_number: int) -> str | None:
    for fn, wt, value in iter_fields(data):
        if fn == field_number and wt == wire_format.WIRETYPE_LENGTH_DELIMITED:
            try:
                return bytes(value).decode("utf-8")
            except UnicodeDecodeError:
                return None
    return None


def get_bytes_fields(data: bytes, field_number: int) -> list[bytes]:
    return [
        bytes(value)
        for fn, wt, value in iter_fields(data)
        if fn == field_number and wt == wire_format.WIRETYPE_LENGTH_DELIMITED
    ]
