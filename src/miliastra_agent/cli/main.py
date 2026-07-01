from pathlib import Path
from typing import Optional

import typer
from rich import print

app = typer.Typer(name="miliastra", help="Miliastra Wonderland automation CLI")


@app.callback()
def main_callback(
    ctx: typer.Context,
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        envvar="MILIastra_PROJECT",
        help="Project under artifacts/projects/ (default: active project)",
    ),
) -> None:
    ctx.ensure_object(dict)
    ctx.obj["project"] = project


def _cli_project(ctx: typer.Context) -> str | None:
    if ctx.obj is None:
        return None
    return ctx.obj.get("project")


@app.command()
def version() -> None:
    """Show package version."""
    from miliastra_agent import __version__

    print(f"miliastra-agent v{__version__}")


@app.command()
def use(
    name: str = typer.Argument(..., help="Project name (creates artifacts/projects/<name>/"),
) -> None:
    """Set the active project and create its artifact directories."""
    from miliastra_agent.paths import get_active_project, set_active_project

    set_active_project(name)
    print(f"[green]Active project:[/green] {name}")
    if get_active_project() != name:
        raise typer.Exit(code=1)


@app.command("projects")
def projects_cmd() -> None:
    """List projects under artifacts/projects/."""
    from miliastra_agent.paths import get_active_project, list_projects

    active = get_active_project()
    names = list_projects()
    if not names:
        print("[yellow]No projects yet.[/yellow] Run: miliastra use my_project")
        return
    for name in names:
        marker = " *" if name == active else ""
        print(f"  {name}{marker}")
    print(f"\nActive: {active}")


@app.command()
def parse(
    ctx: typer.Context,
    path: Path,
    write_json: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Write parsed entities under the project's parsed/ directory",
    ),
    json_out: Path | None = typer.Option(
        None,
        "--json-out",
        help="Custom JSON output path (implies --json)",
    ),
) -> None:
    """Parse a GIL/GIA file and print a summary."""
    from miliastra_agent.parsers.gil import export_parsed, format_summary, parse_gi_file

    if not path.exists():
        raise typer.BadParameter(f"File not found: {path}")

    project = _cli_project(ctx)
    parsed = parse_gi_file(path)
    print(format_summary(parsed))

    if write_json or json_out is not None:
        json_path, summary_path, graphs_path = export_parsed(
            parsed,
            json_out=json_out,
            project=project,
        )
        print(f"[green]Wrote[/green] {json_path}")
        if summary_path is not None:
            print(f"[green]Wrote[/green] {summary_path}")
        if graphs_path is not None:
            print(f"[green]Wrote[/green] {graphs_path}")


@app.command("parse-input")
def parse_input(ctx: typer.Context) -> None:
    """Parse every file in the active project's input/ into parsed/."""
    from miliastra_agent.parsers.gil import export_parsed, parse_gi_file
    from miliastra_agent.paths import get_active_project, iter_input_files

    project = _cli_project(ctx)
    active = project or get_active_project()
    sources = iter_input_files(project)
    if not sources:
        print(
            f"[yellow]No files in artifacts/projects/{active}/input/ "
            "(levels or assets)[/yellow]"
        )
        raise typer.Exit(code=0)

    for source in sources:
        parsed = parse_gi_file(source)
        json_path, summary_path, graphs_path = export_parsed(parsed, project=project)
        detail = f"{parsed.entity_count} entities"
        if parsed.node_graph_count:
            detail += f", {parsed.node_graph_count} graphs ({parsed.node_count} nodes)"
        print(f"[green]Parsed[/green] {source.name} -> {json_path.name} ({detail})")
        if summary_path is not None:
            print(f"          summary -> {summary_path.name}")
        if graphs_path is not None:
            print(f"          graphs  -> {graphs_path.name}")


@app.command("generate-platforms")
def generate_platforms(
    ctx: typer.Context,
    count: int = typer.Option(10, help="Number of platforms"),
    output: Path | None = typer.Option(
        None,
        help="Output .gia path (default: <project>/output/assets/platforms.gia)",
    ),
    template_id: int = typer.Option(20001869, help="Block template ID"),
) -> None:
    """Generate a simple platform course as a .gia asset file."""
    from miliastra_agent.generators.entities import generate_platform_course
    from miliastra_agent.paths import default_platform_output

    out_path = output or default_platform_output(_cli_project(ctx))
    out = generate_platform_course(
        count=count,
        template_id=template_id,
        output_path=out_path,
    )
    print(f"[green]Generated[/green] {count} platforms -> {out}")


if __name__ == "__main__":
    app()
