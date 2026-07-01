"""Load Wu-Yijun node_data.json and resolve kernel IDs to names."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from miliastra_agent.paths import NODE_CATALOG_PATH


def default_catalog_path() -> Path:
    return NODE_CATALOG_PATH


class NodeCatalog:
    """Index over `Nodes[].ID` from community node_data.json."""

    def __init__(self, data: dict) -> None:
        self.version: str = str(data.get("Version", ""))
        self.game_version: str = str(data.get("GameVersion", ""))
        self._by_id: dict[int, dict] = {}
        for node in data.get("Nodes", []):
            node_id = node.get("ID")
            if node_id is not None:
                self._by_id[int(node_id)] = node

    @classmethod
    def load(cls, path: Path | None = None) -> NodeCatalog:
        catalog_path = path or default_catalog_path()
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
        return cls(data)

    def __len__(self) -> int:
        return len(self._by_id)

    def has_kernel(self, kernel_id: int) -> bool:
        return kernel_id in self._by_id

    def get_node(self, kernel_id: int) -> dict | None:
        return self._by_id.get(kernel_id)

    def get_kernel_name(self, kernel_id: int, *, lang: str = "zh-Hans") -> str:
        node = self._by_id.get(kernel_id)
        if node is None:
            return ""
        in_game = node.get("InGameName") or {}
        if isinstance(in_game, dict):
            name = in_game.get(lang) or in_game.get("en")
            if name:
                return str(name)
        identifier = node.get("Identifier")
        return str(identifier) if identifier else ""

    def get_identifier(self, kernel_id: int) -> str:
        node = self._by_id.get(kernel_id)
        if node is None:
            return ""
        return str(node.get("Identifier") or "")


@lru_cache(maxsize=1)
def load_default_catalog() -> NodeCatalog | None:
    path = default_catalog_path()
    if not path.is_file():
        return None
    return NodeCatalog.load(path)


def enrich_graph_nodes(graph: dict, catalog: NodeCatalog | None) -> dict:
    """Add `kernel_name` (and `kernel_identifier`) to each node dict."""
    if catalog is None:
        return graph
    for node in graph.get("nodes") or []:
        kernel_ref = node.get("kernel_ref") or node.get("shell_ref")
        if not kernel_ref:
            continue
        runtime_id = kernel_ref.get("runtime_id")
        if runtime_id is None:
            continue
        kernel_id = int(runtime_id)
        name = catalog.get_kernel_name(kernel_id)
        if name:
            node["kernel_name"] = name
        identifier = catalog.get_identifier(kernel_id)
        if identifier:
            node["kernel_identifier"] = identifier
    return graph
