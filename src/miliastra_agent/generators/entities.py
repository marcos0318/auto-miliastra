"""Programmatic entity and platform generation."""

from __future__ import annotations

from pathlib import Path

from miliastra_agent.core.gi_file import write_gia
from miliastra_agent.core.models import EntityPlacement, Vec3


def generate_platform_course(
    *,
    count: int,
    template_id: int,
    output_path: Path,
    spacing: float = 2.0,
    rise: float = 0.5,
    entity_id_start: int = 1078000000,
) -> Path:
    """Generate stepping platforms along +X with gradual +Y rise.

    Note: payload encoding is minimal for now; full protobuf entity assembly
    will be added in a follow-up iteration (see UGC-File-Generate-Utils).
    """
    placements: list[EntityPlacement] = []
    for i in range(count):
        placements.append(
            EntityPlacement(
                template_id=template_id,
                name=f"Platform_{i}",
                entity_id=entity_id_start + i,
                position=Vec3(x=i * spacing, y=i * rise, z=0.0),
            )
        )

    # Placeholder payload until protobuf entity encoder is integrated.
    payload = _encode_placements_stub(placements)
    return write_gia(output_path, payload)


def _encode_placements_stub(placements: list[EntityPlacement]) -> bytes:
    lines = []
    for p in placements:
        lines.append(
            f"{p.entity_id},{p.template_id},{p.position.x},{p.position.y},{p.position.z}"
        )
    return "\n".join(lines).encode("utf-8")
