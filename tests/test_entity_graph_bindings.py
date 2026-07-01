from pathlib import Path

import pytest

from miliastra_agent.core.gi_file import read_payload
from miliastra_agent.parsers.entity_graph_bindings import parse_gil_entity_graph_bindings
from miliastra_agent.parsers.gil import parse_gi_file


from miliastra_agent.paths import resolve_input_level

GIL_FIXTURE = resolve_input_level("double_gun")


@pytest.mark.skipif(GIL_FIXTURE is None, reason="double_gun.gil not present")
def test_entity_graph_bindings() -> None:
    payload = read_payload(GIL_FIXTURE)
    bindings = parse_gil_entity_graph_bindings(payload)

    assert len(bindings) == 90
    graph_ids = {b.graph_id for b in bindings}
    assert len(graph_ids) == 20
    assert 1073741846 in graph_ids

    level_entity = next(b for b in bindings if b.entity_id == 1094713345)
    assert level_entity.graph_id == 1073741846
    assert level_entity.slot == 1


@pytest.mark.skipif(GIL_FIXTURE is None, reason="double_gun.gil not present")
def test_parsed_gil_includes_bindings_with_names() -> None:
    parsed = parse_gi_file(GIL_FIXTURE)

    assert parsed.entity_graph_binding_count == 90
    level_bindings = [b for b in parsed.entity_graph_bindings if b.entity_id == 1094713345]
    assert len(level_bindings) == 3
    assert any(b.graph_name for b in level_bindings)
