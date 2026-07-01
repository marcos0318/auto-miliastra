"""Tests for node catalog lookup and graph enrichment."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from miliastra_agent.catalog.node_catalog import NodeCatalog, enrich_graph_nodes
from miliastra_agent.paths import NODE_CATALOG_PATH, resolve_input_level

GIL_FIXTURE = resolve_input_level("double_gun")
CATALOG = NODE_CATALOG_PATH


@pytest.mark.skipif(not CATALOG.is_file(), reason="node_data.json not present")
def test_catalog_resolves_kernel_66() -> None:
    catalog = NodeCatalog.load(CATALOG)
    assert catalog.get_kernel_name(66) == "设置预设状态"
    assert catalog.get_identifier(66) == "Execution.Preset_Status.Set_Status"


def test_enrich_graph_nodes_adds_kernel_name() -> None:
    catalog = NodeCatalog(
        {
            "Nodes": [
                {
                    "ID": 66,
                    "Identifier": "Execution.Preset_Status.Set_Status",
                    "InGameName": {"zh-Hans": "设置预设状态", "en": "Set Preset Status"},
                }
            ]
        }
    )
    graph = {
        "display_name": "宝箱",
        "nodes": [
            {
                "index": 1,
                "kernel_ref": {"runtime_id": "66"},
            }
        ],
    }
    enrich_graph_nodes(graph, catalog)
    node = graph["nodes"][0]
    assert node["kernel_name"] == "设置预设状态"
    assert node["kernel_identifier"] == "Execution.Preset_Status.Set_Status"


@pytest.mark.skipif(GIL_FIXTURE is None, reason="double_gun.gil not present")
def test_enriched_export_has_kernel_name() -> None:
    from miliastra_agent.core.gi_file import read_payload
    from miliastra_agent.parsers.node_graphs import parse_gil_node_graphs

    assert GIL_FIXTURE is not None
    payload = read_payload(GIL_FIXTURE)
    catalog = NodeCatalog.load(CATALOG)
    _, export = parse_gil_node_graphs(payload, catalog=catalog)
    first_node = export.graphs[0]["nodes"][0]
    assert "kernel_name" in first_node
    assert first_node["kernel_name"] == catalog.get_kernel_name(66)
