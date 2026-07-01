from pathlib import Path

import typer
from rich import print

app = typer.Typer(name="miliastra", help="Miliastra Wonderland automation CLI")


@app.command()
def version() -> None:
    """Show package version."""
    from miliastra_agent import __version__

    print(f"miliastra-agent v{__version__}")


@app.command()
def parse(path: Path) -> None:
    """Parse a GIL/GIA file and print a summary."""
    from miliastra_agent.parsers.gil import parse_gi_file

    if not path.exists():
        raise typer.BadParameter(f"File not found: {path}")

    summary = parse_gi_file(path)
    print(summary)


@app.command("generate-platforms")
def generate_platforms(
    count: int = typer.Option(10, help="Number of platforms"),
    output: Path = typer.Option(Path("output/platforms.gia"), help="Output .gia path"),
    template_id: int = typer.Option(20001869, help="Block template ID"),
) -> None:
    """Generate a simple platform course as a .gia asset file."""
    from miliastra_agent.generators.entities import generate_platform_course

    out = generate_platform_course(
        count=count,
        template_id=template_id,
        output_path=output,
    )
    print(f"[green]Generated[/green] {count} platforms -> {out}")


if __name__ == "__main__":
    app()
