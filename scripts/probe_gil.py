"""Probe GIL sections for node graph signatures."""
from __future__ import annotations

from pathlib import Path

from google.protobuf.internal import decoder, wire_format

from miliastra_agent.core.gi_file import read_payload
from miliastra_agent.core.wire import get_bytes_fields, get_string, iter_fields
from miliastra_agent.paths import resolve_input_level


def decode_raw(data: bytes, indent: int = 0, max_depth: int = 3, limit: int = 40) -> list[str]:
    pos = 0
    lines: list[str] = []
    prefix = "  " * indent
    count = 0
    while pos < len(data) and count < limit:
        tag, npos = decoder._DecodeVarint(data, pos)
        if npos == pos:
            break
        field_num = tag >> 3
        wire_type = tag & 7
        pos = npos
        count += 1
        if wire_type == wire_format.WIRETYPE_VARINT:
            value, pos = decoder._DecodeVarint(data, pos)
            lines.append(f"{prefix}{field_num}: {value}")
        elif wire_type == wire_format.WIRETYPE_LENGTH_DELIMITED:
            length, pos = decoder._DecodeVarint(data, pos)
            value = data[pos : pos + length]
            pos += length
            if indent < max_depth:
                try:
                    text = value.decode("utf-8")
                    if len(text) < 100 and all(c.isprintable() or c in "\n\r\t" for c in text):
                        lines.append(f'{prefix}{field_num}: "{text}"')
                        continue
                except UnicodeDecodeError:
                    pass
                lines.append(f"{prefix}{field_num} {{  # {length}b")
                lines.extend(decode_raw(value, indent + 1, max_depth, limit=limit))
                lines.append(f"{prefix}}}")
            else:
                lines.append(f"{prefix}{field_num}: <{length}b>")
        else:
            lines.append(f"{prefix}{field_num}: wt={wire_type}")
            break
    return lines


def main() -> None:
    gil = resolve_input_level("double_gun")
    if gil is None:
        raise SystemExit("double_gun.gil not found under artifacts/projects/")
    payload = read_payload(gil)
    print("level:", get_string(payload, 2))
    for field in (4, 6, 10, 15):
        chunks = get_bytes_fields(payload, field)
        if not chunks:
            continue
        chunk = chunks[0]
        sub = get_bytes_fields(chunk, 1)
        print(f"\n=== field {field}: {len(chunk)} bytes, {len(sub)} x field-1 items ===")
        if sub:
            lines = decode_raw(sub[0], max_depth=4, limit=60)
            print("\n".join(lines[:50]))


if __name__ == "__main__":
    main()
