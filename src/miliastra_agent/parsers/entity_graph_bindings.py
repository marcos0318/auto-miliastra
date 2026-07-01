"""Extract entity ↔ node graph bindings from GIL logic entities."""

from __future__ import annotations

from miliastra_agent.core.graph_models import EntityGraphBinding
from miliastra_agent.core.wire import get_bytes_fields, get_string, get_varint


def _name_from_entity(data: bytes) -> str:
    for prop in get_bytes_fields(data, 5):
        name_chunks = get_bytes_fields(prop, 11)
        if name_chunks:
            name = get_string(name_chunks[0], 1)
            if name:
                return name
    return ""


def _graph_refs_from_component(blob: bytes) -> list[tuple[int | None, int, int | None]]:
    """Parse component field 13 bytes into (slot, graph_id, field_501) tuples."""
    refs: list[tuple[int | None, int, int | None]] = []
    for outer in get_bytes_fields(blob, 1):
        for inner in get_bytes_fields(outer, 1):
            slot = get_varint(inner, 1)
            graph_id = get_varint(inner, 2)
            extra = get_varint(inner, 501)
            if graph_id is not None:
                refs.append((slot, graph_id, extra))
    return refs


def parse_gil_entity_graph_bindings(payload: bytes) -> list[EntityGraphBinding]:
    """Parse graph attachments from GIL field 5 logic entities (component type 3)."""
    bindings: list[EntityGraphBinding] = []

    for chunk in get_bytes_fields(payload, 5):
        for entity in get_bytes_fields(chunk, 1):
            entity_id = get_varint(entity, 1)
            if entity_id is None:
                continue
            entity_name = _name_from_entity(entity)

            for comp in get_bytes_fields(entity, 6):
                if get_varint(comp, 1) != 3:
                    continue
                blobs = get_bytes_fields(comp, 13)
                if not blobs:
                    continue
                for slot, graph_id, field_501 in _graph_refs_from_component(blobs[0]):
                    bindings.append(
                        EntityGraphBinding(
                            entity_id=entity_id,
                            entity_name=entity_name,
                            graph_id=graph_id,
                            slot=slot,
                            field_501=field_501,
                        )
                    )

    return bindings
