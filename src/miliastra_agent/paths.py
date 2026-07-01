"""Conventional paths for local artifacts (per-project input / parsed / output)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ROOT = REPO_ROOT / "artifacts"
PROJECTS_DIR = ARTIFACTS_ROOT / "projects"
ACTIVE_PROJECT_FILE = ARTIFACTS_ROOT / "active_project"
DEFAULT_PROJECT = "default"

CATALOG_DIR = ARTIFACTS_ROOT / "catalog"
NODE_CATALOG_PATH = CATALOG_DIR / "node_data.json"

# Legacy flat layout (pre-project refactor)
LEGACY_INPUT_DIR = ARTIFACTS_ROOT / "input"
LEGACY_PARSED_DIR = ARTIFACTS_ROOT / "parsed"
LEGACY_OUTPUT_DIR = ARTIFACTS_ROOT / "output"
LEGACY_INPUT_LEVELS = LEGACY_INPUT_DIR / "levels"
LEGACY_PARSED_LEVELS = LEGACY_PARSED_DIR / "levels"


def get_active_project() -> str:
    if ACTIVE_PROJECT_FILE.is_file():
        name = ACTIVE_PROJECT_FILE.read_text(encoding="utf-8").strip()
        if name:
            return name
    env = os.environ.get("MILIastra_PROJECT", "").strip()
    if env:
        return env
    return DEFAULT_PROJECT


def set_active_project(name: str) -> None:
    name = name.strip()
    if not name:
        raise ValueError("project name must not be empty")
    ACTIVE_PROJECT_FILE.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE_PROJECT_FILE.write_text(f"{name}\n", encoding="utf-8")
    ProjectPaths(name).ensure_dirs()


def list_projects() -> list[str]:
    if not PROJECTS_DIR.is_dir():
        return []
    return sorted(
        p.name
        for p in PROJECTS_DIR.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    )


def infer_project_from_path(path: Path) -> str | None:
    """Return project name if path lives under artifacts/projects/<name>/."""
    try:
        rel = path.resolve().relative_to(PROJECTS_DIR.resolve())
        if rel.parts:
            return rel.parts[0]
    except ValueError:
        pass
    return None


def project_for_source(source: Path, *, override: str | None = None) -> str:
    if override:
        return override
    inferred = infer_project_from_path(source)
    if inferred:
        return inferred
    return get_active_project()


@dataclass(frozen=True)
class ProjectPaths:
    project: str

    @property
    def root(self) -> Path:
        return PROJECTS_DIR / self.project

    @property
    def input_dir(self) -> Path:
        return self.root / "input"

    @property
    def parsed_dir(self) -> Path:
        return self.root / "parsed"

    @property
    def output_dir(self) -> Path:
        return self.root / "output"

    @property
    def input_levels(self) -> Path:
        return self.input_dir / "levels"

    @property
    def input_assets(self) -> Path:
        return self.input_dir / "assets"

    @property
    def parsed_levels(self) -> Path:
        return self.parsed_dir / "levels"

    @property
    def parsed_assets(self) -> Path:
        return self.parsed_dir / "assets"

    @property
    def output_levels(self) -> Path:
        return self.output_dir / "levels"

    @property
    def output_assets(self) -> Path:
        return self.output_dir / "assets"

    def ensure_dirs(self) -> None:
        for path in (
            self.input_levels,
            self.input_assets,
            self.parsed_levels,
            self.parsed_assets,
            self.output_levels,
            self.output_assets,
        ):
            path.mkdir(parents=True, exist_ok=True)

    def parsed_json_path(self, source: Path) -> Path:
        self.ensure_dirs()
        stem = source.stem
        if source.suffix.lower() in {".gil", ".gir"}:
            return self.parsed_levels / f"{stem}.json"
        return self.parsed_assets / f"{stem}.json"

    def parsed_summary_path(self, source: Path) -> Path:
        json_path = self.parsed_json_path(source)
        return json_path.with_name(f"{json_path.stem}.summary.txt")

    def parsed_graphs_json_path(self, source: Path) -> Path:
        return self.parsed_json_path(source).with_name(f"{source.stem}.graphs.json")

    def iter_input_files(self) -> list[Path]:
        self.ensure_dirs()
        files: list[Path] = []
        for pattern in ("*.gil", "*.gir"):
            files.extend(sorted(self.input_levels.glob(pattern)))
        for pattern in ("*.gia", "*.gip"):
            files.extend(sorted(self.input_assets.glob(pattern)))
        return files


def project_paths(project: str | None = None) -> ProjectPaths:
    return ProjectPaths(project or get_active_project())


def parsed_json_path(source: Path, *, project: str | None = None) -> Path:
    proj = project_for_source(source, override=project)
    return ProjectPaths(proj).parsed_json_path(source)


def parsed_summary_path(source: Path, *, project: str | None = None) -> Path:
    proj = project_for_source(source, override=project)
    return ProjectPaths(proj).parsed_summary_path(source)


def parsed_graphs_json_path(source: Path, *, project: str | None = None) -> Path:
    proj = project_for_source(source, override=project)
    return ProjectPaths(proj).parsed_graphs_json_path(source)


def iter_input_files(project: str | None = None) -> list[Path]:
    return project_paths(project).iter_input_files()


def resolve_input_level(name: str, *, project: str | None = None) -> Path | None:
    """Locate a level .gil for tests/scripts (project layout, then legacy)."""
    stem = name if name.endswith(".gil") else f"{name}.gil"
    candidates: list[Path] = []
    if project:
        candidates.append(ProjectPaths(project).input_levels / stem)
    active = get_active_project()
    candidates.append(ProjectPaths(active).input_levels / stem)
    candidates.extend(
        [
            LEGACY_INPUT_LEVELS / stem,
            ARTIFACTS_ROOT / stem,
        ]
    )
    for path in candidates:
        if path.is_file():
            return path
    return None


def default_platform_output(project: str | None = None) -> Path:
    return project_paths(project).output_assets / "platforms.gia"
