"""Programmatic entity and platform generation."""

from __future__ import annotations

from pathlib import Path

from miliastra_agent.core.gi_file import write_gia
from miliastra_agent.core.models import EntityPlacement, Vec3
from miliastra_agent.generators.gia_encode import encode_gia_payload


def generate_platform_course(
    *,
    count: int,
    template_id: int,
    output_path: Path,
    spacing: float = 2.0,
    rise: float = 0.5,
    entity_id_start: int = 1078000000,
) -> Path:
    """Generate stepping platforms along +X with gradual +Y rise."""
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

    payload = encode_gia_payload(placements, entity_id_start=entity_id_start)
    return write_gia(output_path, payload)
