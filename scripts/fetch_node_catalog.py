"""Download node catalog (data.json) from Wu-Yijun node editor pack."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CATALOG_OUT = REPO / "artifacts" / "catalog" / "node_data.json"
UPSTREAM = (
    "https://github.com/Wu-Yijun/"
    "Genshin-Impact-Miliastra-Wonderland-Code-Node-Editor-Pack.git"
)
UPSTREAM_REL = "utils/node_data/data.json"


def fetch(*, dest: Path = CATALOG_OUT) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="miliastra-node-catalog-") as tmp:
        clone_dir = Path(tmp) / "pack"
        subprocess.run(
            ["git", "clone", "--depth", "1", UPSTREAM, str(clone_dir)],
            check=True,
        )
        src = clone_dir / UPSTREAM_REL
        if not src.is_file():
            raise FileNotFoundError(f"Expected catalog at {src}")
        shutil.copy2(src, dest)
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=CATALOG_OUT,
        help=f"Output path (default: {CATALOG_OUT.relative_to(REPO)})",
    )
    args = parser.parse_args()
    path = fetch(dest=args.out)
    print(f"Wrote {path} ({path.stat().st_size // 1024} KiB)")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"git clone failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
