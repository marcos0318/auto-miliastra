from pathlib import Path

import pytest

from miliastra_agent.core.gi_file import read_header, read_payload
from miliastra_agent.parsers.gil import parse_gi_file


from miliastra_agent.paths import resolve_input_level

GIL_FIXTURE = resolve_input_level("double_gun")


@pytest.mark.skipif(GIL_FIXTURE is None, reason="double_gun.gil not present")
def test_parse_double_gun_gil() -> None:
    parsed = parse_gi_file(GIL_FIXTURE)

    assert parsed.header.type_name == "GIL"
    assert parsed.level_name == "TPS搜打撤"
    assert parsed.entity_count == 752
    assert parsed.node_graph_count == 81
    assert parsed.node_count == 1392

    with_transform = [e for e in parsed.entities if e.position.x or e.position.y or e.position.z]
    assert len(with_transform) > 100

    decoration = next(e for e in parsed.entities if e.name.startswith("装饰物"))
    assert decoration.template_id > 0
    assert decoration.entity_id is not None


@pytest.mark.skipif(GIL_FIXTURE is None, reason="double_gun.gil not present")
def test_gil_payload_sections() -> None:
    payload = read_payload(GIL_FIXTURE)
    header = read_header(GIL_FIXTURE.read_bytes())

    assert header.file_type == 2
    assert len(payload) == header.content_length
