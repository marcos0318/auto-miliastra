"""Pydantic models for node graph exports."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ResourceLocatorModel(BaseModel):
    source_domain: int | None = None
    service_domain: int | None = None
    kind: int | None = None
    asset_guid: int | None = None
    runtime_id: int | None = None


class NodeGraphSummary(BaseModel):
    graph_id: int
    display_name: str = ""
    node_count: int = 0
    blackboard_count: int = 0
    comment_count: int = 0


class EntityGraphBinding(BaseModel):
    """Link between a logic entity and a node graph runtime_id."""

    entity_id: int
    entity_name: str = ""
    graph_id: int
    graph_name: str = ""
    slot: int | None = None
    field_501: int | None = None


class NodeGraphExport(BaseModel):
    """Full node graph bundle for a GIL level."""

    level_name: str = ""
    graph_count: int = 0
    total_nodes: int = 0
    graphs: list[dict] = Field(default_factory=list)
