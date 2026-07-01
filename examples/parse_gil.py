"""Example: parse a GIL/GIA file."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from miliastra_agent.parsers.gil import format_summary, parse_gi_file


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    print(format_summary(parse_gi_file(args.path)))


if __name__ == "__main__":
    main()
