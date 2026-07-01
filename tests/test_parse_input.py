from pathlib import Path

import pytest
from typer.testing import CliRunner

from miliastra_agent.cli.main import app
from miliastra_agent.parsers.gil import export_parsed, parse_gi_file
from miliastra_agent.paths import project_paths, resolve_input_level

GIL_FIXTURE = resolve_input_level("double_gun")


@pytest.mark.skipif(GIL_FIXTURE is None, reason="double_gun.gil not present")
def test_export_parsed_writes_json_and_summary(tmp_path: Path) -> None:
    assert GIL_FIXTURE is not None
    parsed = parse_gi_file(GIL_FIXTURE)
    json_path, summary_path, graphs_path = export_parsed(parsed, json_out=tmp_path / "out.json")

    assert json_path.exists()
    assert summary_path is not None and summary_path.exists()
    assert "entities" in json_path.read_text(encoding="utf-8")
    assert "Entities:" in summary_path.read_text(encoding="utf-8")
    assert graphs_path is not None and graphs_path.exists()


@pytest.mark.skipif(GIL_FIXTURE is None, reason="double_gun.gil not present")
def test_parse_input_command() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["parse-input"])
    assert result.exit_code == 0
    parsed_levels = project_paths("double_gun").parsed_levels
    assert (parsed_levels / "double_gun.json").exists()
    assert (parsed_levels / "double_gun.summary.txt").exists()
    assert (parsed_levels / "double_gun.graphs.json").exists()
