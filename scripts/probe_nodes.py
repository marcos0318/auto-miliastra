"""Probe inner structure of GIL field 10 graphs."""
from __future__ import annotations

from pathlib import Path

from google.protobuf.internal import wire_format
from google.protobuf import text_format

from miliastra_agent.core.gi_file import read_payload
from miliastra_agent.core.wire import get_bytes_fields, get_string, get_varint, iter_fields
from miliastra_agent.paths import resolve_input_level


def dump_fields(data: bytes, indent: int = 0, depth: int = 0, max_depth: int = 4) -> None:
    prefix = "  " * indent
    for fn, wt, val in iter_fields(data):
        if wt == wire_format.WIRETYPE_VARINT:
            print(f"{prefix}{fn}: {val}")
        elif wt == wire_format.WIRETYPE_LENGTH_DELIMITED:
            raw = bytes(val)
            try:
                text = raw.decode("utf-8")
                if len(text) < 120 and all(c.isprintable() or c in "\n\r\t" for c in text):
                    print(f'{prefix}{fn}: "{text}"')
                    continue
            except UnicodeDecodeError:
                pass
            if depth < max_depth:
                print(f"{prefix}{fn} {{")
                dump_fields(raw, indent + 1, depth + 1, max_depth)
                print(f"{prefix}}}")
            else:
                print(f"{prefix}{fn}: <{len(raw)} bytes>")
        elif wt == wire_format.WIRETYPE_FIXED32:
            import struct

            print(f"{prefix}{fn}: {struct.unpack('<f', bytes(val))[0]}")


def try_nodegraph_proto(inner: bytes) -> None:
    # Attempt Wu-Yijun style wrappers after we vendor protos
    try:
        from miliastra_agent.core.proto_gen import node_graph_pb2 as ng

        for parser in (
            lambda b: ng.NodeGraphContainer.FromString(b),
            lambda b: ng.NodeGraph.FromString(b),
            lambda b: ng.ResourceEntry.FromString(b),
        ):
            try:
                msg = parser(inner)
                print("PARSED AS", type(msg).__name__)
                print(text_format.MessageToString(msg, as_utf8=True)[:2000])
                return
            except Exception:
                pass
    except ImportError:
        pass
    print("proto parse not available yet")


def main() -> None:
    gil = resolve_input_level("double_gun")
    if gil is None:
        raise SystemExit("double_gun.gil not found under artifacts/projects/")
    payload = read_payload(gil)
    items = get_bytes_fields(get_bytes_fields(payload, 10)[0], 1)
    inner = get_bytes_fields(items[0], 1)[0]
    print("inner bytes", len(inner))
    print("--- wire dump ---")
    dump_fields(inner, max_depth=5)
    print("--- proto try ---")
    try_nodegraph_proto(inner)


if __name__ == "__main__":
    main()
