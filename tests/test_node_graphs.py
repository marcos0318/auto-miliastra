from pathlib import Path

import pytest

from miliastra_agent.core.gi_file import read_payload
from miliastra_agent.parsers.gil import export_parsed, parse_gi_file
from miliastra_agent.parsers.node_graphs import parse_gil_node_graphs


from miliastra_agent.paths import resolve_input_level

GIL_FIXTURE = resolve_input_level("double_gun")


@pytest.mark.skipif(GIL_FIXTURE is None, reason="double_gun.gil not present")
def test_parse_gil_node_graphs() -> None:
    payload = read_payload(GIL_FIXTURE)
    summaries, export = parse_gil_node_graphs(payload)

    assert len(summaries) == 81
    assert export.graph_count == 81
    assert export.total_nodes == 1392
    assert summaries[0].graph_id == 1073741825
    assert summaries[0].node_count == 7
    assert len(export.graphs[0]["nodes"]) == 7
    first = export.graphs[0]["nodes"][0]
    if "kernel_name" in first:
        assert first["kernel_name"] == "设置预设状态"


@pytest.mark.skipif(GIL_FIXTURE is None, reason="double_gun.gil not present")
def test_parsed_gi_file_includes_graph_summaries() -> None:
    parsed = parse_gi_file(GIL_FIXTURE)
    assert parsed.node_graph_count == 81
    assert parsed.node_count == 1392


@pytest.mark.skipif(GIL_FIXTURE is None, reason="double_gun.gil not present")
def test_export_writes_graphs_json(tmp_path: Path) -> None:
    parsed = parse_gi_file(GIL_FIXTURE)
    json_path, _, graphs_path = export_parsed(
        parsed,
        json_out=tmp_path / "out.json",
    )
    assert json_path.exists()
    assert graphs_path is not None and graphs_path.exists()
    assert "nodes" in graphs_path.read_text(encoding="utf-8")
