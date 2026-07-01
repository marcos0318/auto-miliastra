"""Probe component type 3 (field_13) graph bindings."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from miliastra_agent.core.gi_file import read_payload
from miliastra_agent.core.wire import get_bytes_fields, get_string, get_varint, iter_fields
from miliastra_agent.paths import resolve_input_level
from miliastra_agent.parsers.node_graphs import parse_gil_node_graphs


def extract_graph_refs(blob: bytes) -> list[dict]:
    refs: list[dict] = []
    for outer in get_bytes_fields(blob, 1):
        for inner in get_bytes_fields(outer, 1):
            slot = get_varint(inner, 1)
            graph_id = get_varint(inner, 2)
            extra = get_varint(inner, 501)
            if graph_id is not None:
                refs.append({"slot": slot, "graph_id": graph_id, "field_501": extra})
    return refs


def main() -> None:
    gil = resolve_input_level("double_gun")
    if gil is None:
        raise SystemExit("double_gun.gil not found under artifacts/projects/")
    payload = read_payload(gil)
    summaries, _ = parse_gil_node_graphs(payload)
    graph_names = {s.graph_id: s.display_name for s in summaries}

    bindings: list[dict] = []
    comp3_count = 0
    ref_counts: Counter[int] = Counter()

    for chunk in get_bytes_fields(payload, 5):
        for ent in get_bytes_fields(chunk, 1):
            eid = get_varint(ent, 1) or 0
            name = ""
            for prop in get_bytes_fields(ent, 5):
                n = get_string(get_bytes_fields(prop, 11)[0], 1) if get_bytes_fields(prop, 11) else None
                if n:
                    name = n
            for comp in get_bytes_fields(ent, 6):
                ctype = get_varint(comp, 1)
                if ctype != 3:
                    continue
                comp3_count += 1
                blobs = get_bytes_fields(comp, 13)
                if not blobs:
                    continue
                refs = extract_graph_refs(blobs[0])
                for r in refs:
                    ref_counts[r["graph_id"]] += 1
                    bindings.append(
                        {
                            "entity_id": eid,
                            "entity_name": name,
                            "graph_id": r["graph_id"],
                            "graph_name": graph_names.get(r["graph_id"], ""),
                            "slot": r["slot"],
                        }
                    )

    print(f"logic entities with component type 3: {comp3_count}")
    print(f"total graph refs: {len(bindings)}")
    print(f"unique graphs referenced: {len(ref_counts)}")
    print(f"graphs in field10: {len(graph_names)}")
    missing = set(ref_counts) - set(graph_names)
    print(f"refs not in field10: {len(missing)} sample {sorted(missing)[:5]}")

    print("\nSample bindings:")
    for b in bindings[:12]:
        print(f"  {b['entity_name']} ({b['entity_id']}) -> {b['graph_name'] or '?'} ({b['graph_id']}) slot={b['slot']}")

    print("\nTop referenced graphs:")
    for gid, cnt in ref_counts.most_common(8):
        print(f"  {graph_names.get(gid, '?')} ({gid}): {cnt} entities")


if __name__ == "__main__":
    main()
