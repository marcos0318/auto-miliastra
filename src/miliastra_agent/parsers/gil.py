"""Parse GI container files (.gil / .gia) and extract entity data."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from miliastra_agent.core.gi_file import read_header, read_payload
from miliastra_agent.core.graph_models import EntityGraphBinding, NodeGraphSummary
from miliastra_agent.core.models import EntityPlacement, GiFileHeader
from miliastra_agent.parsers.entities import parse_payload
from miliastra_agent.parsers.entity_graph_bindings import parse_gil_entity_graph_bindings
from miliastra_agent.parsers.node_graphs import parse_gil_node_graphs


class ParsedGiFile(BaseModel):
    path: Path
    header: GiFileHeader
    level_name: str = ""
    entities: list[EntityPlacement] = Field(default_factory=list)
    node_graphs: list[NodeGraphSummary] = Field(default_factory=list)
    entity_graph_bindings: list[EntityGraphBinding] = Field(default_factory=list)

    @property
    def entity_count(self) -> int:
        return len(self.entities)

    @property
    def node_graph_count(self) -> int:
        return len(self.node_graphs)

    @property
    def node_count(self) -> int:
        return sum(g.node_count for g in self.node_graphs)

    @property
    def entity_graph_binding_count(self) -> int:
        return len(self.entity_graph_bindings)


def parse_gi_file(path: Path) -> ParsedGiFile:
    data = path.read_bytes()
    header = read_header(data)
    payload = read_payload(path)
    entities = parse_payload(payload, file_type=header.file_type)

    level_name = ""
    node_graphs: list[NodeGraphSummary] = []
    entity_graph_bindings: list[EntityGraphBinding] = []
    if header.file_type == 2:
        from miliastra_agent.core.wire import get_string

        level_name = get_string(payload, 2) or ""
        node_graphs, _ = parse_gil_node_graphs(payload)
        entity_graph_bindings = parse_gil_entity_graph_bindings(payload)
        graph_names = {g.graph_id: g.display_name for g in node_graphs}
        for binding in entity_graph_bindings:
            binding.graph_name = graph_names.get(binding.graph_id, "")

    return ParsedGiFile(
        path=path,
        header=header,
        level_name=level_name,
        entities=entities,
        node_graphs=node_graphs,
        entity_graph_bindings=entity_graph_bindings,
    )


def format_summary(parsed: ParsedGiFile, *, limit: int = 20) -> str:
    header = parsed.header
    lines = [
        f"File: {parsed.path.name}",
        f"Type: {header.type_name}",
        f"Version: {header.version}",
        f"Payload size: {header.content_length} bytes",
    ]
    if parsed.level_name:
        lines.append(f"Level: {parsed.level_name}")
    lines.append(f"Entities: {parsed.entity_count}")
    if parsed.node_graph_count:
        lines.append(f"Node graphs: {parsed.node_graph_count} ({parsed.node_count} nodes total)")
        lines.append("")
        lines.append("Sample node graphs:")
        for graph in parsed.node_graphs[:limit]:
            name = graph.display_name or f"Graph_{graph.graph_id}"
            lines.append(
                f"  - {name} (id={graph.graph_id}, nodes={graph.node_count})"
            )
        if parsed.node_graph_count > limit:
            lines.append(f"  ... and {parsed.node_graph_count - limit} more")

    if parsed.entity_graph_binding_count:
        lines.append("")
        lines.append(f"Entity-graph bindings: {parsed.entity_graph_binding_count}")
        lines.append("Sample bindings:")
        for binding in parsed.entity_graph_bindings[:limit]:
            graph = binding.graph_name or f"Graph_{binding.graph_id}"
            lines.append(
                f"  - {binding.entity_name} (id={binding.entity_id}) -> {graph} (id={binding.graph_id})"
            )
        if parsed.entity_graph_binding_count > limit:
            lines.append(f"  ... and {parsed.entity_graph_binding_count - limit} more")

    if parsed.entities:
        lines.append("")
        lines.append("Sample placements:")
        for entity in parsed.entities[:limit]:
            pos = entity.position
            lines.append(
                f"  - {entity.name} (id={entity.entity_id}, tpl={entity.template_id}) "
                f"@ ({pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f})"
            )
        if parsed.entity_count > limit:
            lines.append(f"  ... and {parsed.entity_count - limit} more")

    return "\n".join(lines)


def export_parsed(
    parsed: ParsedGiFile,
    *,
    json_out: Path | None = None,
    write_summary: bool = True,
    project: str | None = None,
) -> tuple[Path, Path | None, Path | None]:
    """Write parsed results under artifacts/projects/<project>/parsed/.

    Returns (entities_json_path, summary_path, graphs_json_path).
    """
    from miliastra_agent.core.gi_file import read_payload
    from miliastra_agent.paths import parsed_graphs_json_path, parsed_json_path
    from miliastra_agent.parsers.node_graphs import parse_gil_node_graphs_full

    json_path = json_out or parsed_json_path(parsed.path, project=project)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(parsed.model_dump_json(indent=2), encoding="utf-8")

    summary_path: Path | None = None
    if write_summary:
        summary_path = json_path.with_name(f"{json_path.stem}.summary.txt")
        summary_path.write_text(format_summary(parsed), encoding="utf-8")

    graphs_path: Path | None = None
    if parsed.header.file_type == 2 and parsed.node_graph_count:
        payload = read_payload(parsed.path)
        graphs_export = parse_gil_node_graphs_full(payload, level_name=parsed.level_name)
        graphs_path = parsed_graphs_json_path(parsed.path, project=project)
        graphs_path.write_text(graphs_export.model_dump_json(indent=2), encoding="utf-8")

    return json_path, summary_path, graphs_path
