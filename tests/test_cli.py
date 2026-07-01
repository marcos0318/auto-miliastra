from typer.testing import CliRunner

from miliastra_agent.cli.main import app


def test_version() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "miliastra-agent v0.1.0" in result.stdout


def test_parse_missing_file() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["parse", "nonexistent.gil"])
    assert result.exit_code != 0
