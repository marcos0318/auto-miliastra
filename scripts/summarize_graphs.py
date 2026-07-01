"""Summarize parsed node graphs with Chinese kernel names from the catalog."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from miliastra_agent.catalog.node_catalog import NodeCatalog, default_catalog_path
from miliastra_agent.paths import project_paths, resolve_input_level


def _kernel_id(node: dict) -> int | None:
    ref = node.get("kernel_ref") or node.get("shell_ref")
    if not ref:
        return None
    runtime_id = ref.get("runtime_id")
    return int(runtime_id) if runtime_id is not None else None


def format_graph_summary(graph: dict, catalog: NodeCatalog | None) -> list[str]:
    identity = graph.get("identity") or {}
    graph_id = identity.get("runtime_id", "?")
    name = graph.get("display_name") or f"Graph_{graph_id}"
    nodes = graph.get("nodes") or []
    lines = [f"## {name} (id={graph_id}, {len(nodes)} nodes)"]

    for node in sorted(nodes, key=lambda n: n.get("index", 0)):
        idx = node.get("index", "?")
        kernel_id = _kernel_id(node)
        label = node.get("kernel_name")
        if not label and catalog and kernel_id is not None:
            label = catalog.get_kernel_name(kernel_id)
        if not label and kernel_id is not None:
            label = f"kernel_{kernel_id}"
        identifier = node.get("kernel_identifier")
        if not identifier and catalog and kernel_id is not None:
            identifier = catalog.get_identifier(kernel_id)
        extra = f" [{identifier}]" if identifier else ""
        lines.append(f"  {idx}. {label} (id={kernel_id}){extra}")

    return lines


def summarize(
    graphs_path: Path,
    catalog: NodeCatalog | None,
    *,
    graph_limit: int | None = None,
) -> str:
    data = json.loads(graphs_path.read_text(encoding="utf-8"))
    graphs = data.get("graphs") or []
    level = data.get("level_name") or graphs_path.stem.replace(".graphs", "")

    if graph_limit is not None:
        graphs = graphs[:graph_limit]

    unknown: Counter[int] = Counter()
    labeled = 0
    total = 0
    for graph in data.get("graphs") or []:
        for node in graph.get("nodes") or []:
            total += 1
            kernel_id = _kernel_id(node)
            if kernel_id is None:
                continue
            if node.get("kernel_name") or (catalog and catalog.has_kernel(kernel_id)):
                labeled += 1
            else:
                unknown[kernel_id] += 1

    lines = [
        f"# Node graph summary: {level}",
        f"Source: {graphs_path}",
        f"Graphs: {data.get('graph_count', len(graphs))}, "
        f"Nodes: {data.get('total_nodes', total)}",
    ]
    if catalog:
        lines.append(
            f"Catalog: {default_catalog_path()} "
            f"(v{catalog.version}, game {catalog.game_version}, {len(catalog)} nodes)"
        )
    lines.append(f"Labeled kernels: {labeled}/{total}")
    if unknown:
        top = ", ".join(str(k) for k, _ in unknown.most_common(8))
        lines.append(f"Unknown kernel IDs (top): {top}")
    lines.append("")

    for graph in graphs:
        lines.extend(format_graph_summary(graph, catalog))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    default_graphs = project_paths().parsed_levels / "double_gun.graphs.json"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "graphs",
        nargs="?",
        type=Path,
        default=default_graphs,
        help=f"Parsed graphs JSON (default: active project's double_gun.graphs.json)",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=None,
        help="Override node_data.json path",
    )
    parser.add_argument(
        "-o",
        "--out",
        type=Path,
        default=None,
        help="Write summary to file instead of stdout",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only include first N graphs in output",
    )
    args = parser.parse_args(argv)

    if not args.graphs.is_file():
        print(f"Graphs file not found: {args.graphs}", file=sys.stderr)
        return 1

    catalog_path = args.catalog or default_catalog_path()
    catalog: NodeCatalog | None = None
    if catalog_path.is_file():
        catalog = NodeCatalog.load(catalog_path)
    else:
        print(f"Warning: catalog not found at {catalog_path}", file=sys.stderr)

    text = summarize(args.graphs, catalog, graph_limit=args.limit)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
