"""Parse GI container files and extract basic metadata."""

from __future__ import annotations

from pathlib import Path

from miliastra_agent.core.gi_file import read_header, read_payload


def parse_gi_file(path: Path) -> str:
    data = path.read_bytes()
    header = read_header(data)
    payload = read_payload(path)

    lines = [
        f"File: {path.name}",
        f"Type: {header.type_name}",
        f"Version: {header.version}",
        f"Payload size: {len(payload)} bytes",
        f"Total size: {len(data)} bytes",
    ]
    return "\n".join(lines)
