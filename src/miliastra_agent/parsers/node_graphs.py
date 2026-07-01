"""Parse node graphs from GIL level saves (field 10)."""

from __future__ import annotations

from google.protobuf import json_format

from miliastra_agent.catalog.node_catalog import enrich_graph_nodes, load_default_catalog
from miliastra_agent.core.graph_models import NodeGraphExport, NodeGraphSummary
from miliastra_agent.core.proto_gen import gia_graph_pb2 as graph_pb
from miliastra_agent.core.wire import get_bytes_fields


def _summary_from_graph(graph: graph_pb.NodeGraph) -> NodeGraphSummary:
    graph_id = int(graph.identity.runtime_id) if graph.HasField("identity") else 0
    return NodeGraphSummary(
        graph_id=graph_id,
        display_name=graph.display_name,
        node_count=len(graph.nodes),
        blackboard_count=len(graph.blackboard),
        comment_count=len(graph.comments),
    )


def _parse_graph_bytes(data: bytes) -> graph_pb.NodeGraph:
    graph = graph_pb.NodeGraph()
    graph.ParseFromString(data)
    return graph


def parse_gil_node_graphs(
    payload: bytes,
    *,
    catalog=None,
) -> tuple[list[NodeGraphSummary], NodeGraphExport]:
    """Extract NodeGraph messages from GIL payload field 10."""
    summaries: list[NodeGraphSummary] = []
    graph_dicts: list[dict] = []

    if catalog is None:
        catalog = load_default_catalog()

    field10 = get_bytes_fields(payload, 10)
    if not field10:
        return summaries, NodeGraphExport()

    for wrapper in get_bytes_fields(field10[0], 1):
        inner_chunks = get_bytes_fields(wrapper, 1)
        if not inner_chunks:
            continue
        graph = _parse_graph_bytes(inner_chunks[0])
        summaries.append(_summary_from_graph(graph))
        graph_dict = json_format.MessageToDict(
            graph,
            preserving_proto_field_name=True,
            use_integers_for_enums=True,
        )
        enrich_graph_nodes(graph_dict, catalog)
        graph_dicts.append(graph_dict)

    total_nodes = sum(s.node_count for s in summaries)
    export = NodeGraphExport(
        graph_count=len(summaries),
        total_nodes=total_nodes,
        graphs=graph_dicts,
    )
    return summaries, export


def parse_gil_node_graphs_full(payload: bytes, *, level_name: str = "") -> NodeGraphExport:
    _, export = parse_gil_node_graphs(payload)
    export.level_name = level_name
    return export
