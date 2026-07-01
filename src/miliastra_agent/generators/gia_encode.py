"""Encode EntityPlacement models into GIA protobuf payloads.

Logic ported from UGC-File-Generate-Utils ``assembler/block_assembler.py``:
https://github.com/luern0313/UGC-File-Generate-Utils
"""

from __future__ import annotations

from miliastra_agent.core.models import EntityPlacement, Vec3
from miliastra_agent.core.proto_gen import asset_pb2, entity_pb2, gia_pb2

_TRANSFORM_FIELD_501 = 4294967295  # -1 as uint32, required by game format


class EntityEncoder:
    """Build GIACollection payloads from placement models."""

    def __init__(self, entity_id_start: int = 1078000000) -> None:
        self.entity_id_start = entity_id_start
        self._next_entity_id = entity_id_start

    def reset_entity_id(self, start_id: int | None = None) -> None:
        self._next_entity_id = start_id if start_id is not None else self.entity_id_start

    def encode_payload(self, placements: list[EntityPlacement]) -> bytes:
        collection = gia_pb2.GIACollection()
        for placement in placements:
            collection.Assets.append(self._build_asset(placement))
        return collection.SerializeToString()

    def _allocate_entity_id(self, placement: EntityPlacement) -> int:
        if placement.entity_id is not None:
            return placement.entity_id
        entity_id = self._next_entity_id
        self._next_entity_id += 1
        return entity_id

    def _build_asset(self, placement: EntityPlacement) -> asset_pb2.Asset:
        entity_id = self._allocate_entity_id(placement)
        entity_name = placement.name or f"Entity_{entity_id}"

        entity_data = entity_pb2.Entity(
            data=self._build_entity_data(placement, entity_id),
            field_2=0,
            template_id=placement.template_id,
        )
        meta = asset_pb2.AssetMeta(
            field_2=1,
            meta_type=asset_pb2.AssetMeta.AssetMetaType.ENTITY,
            asset_id=entity_id,
        )
        return asset_pb2.Asset(
            meta=meta,
            name=entity_name,
            type=asset_pb2.Asset.AssetType.ENTITY,
            entity_data=entity_data,
        )

    def _build_entity_data(self, placement: EntityPlacement, entity_id: int) -> entity_pb2.EntityData:
        data = entity_pb2.EntityData(
            entity_id=entity_id,
            template=entity_pb2.TemplateReference(
                template_id=placement.template_id,
                field_2=1,
            ),
            template_id_ref=placement.template_id,
        )
        if placement.name:
            data.properties.append(_name_property(placement.name))
        data.components.append(_transform_component(placement))
        return data


def encode_gia_payload(
    placements: list[EntityPlacement],
    *,
    entity_id_start: int = 1078000000,
) -> bytes:
    """Serialize placements into a GIACollection protobuf payload."""
    return EntityEncoder(entity_id_start=entity_id_start).encode_payload(placements)


def _name_property(name: str) -> entity_pb2.Property:
    return entity_pb2.Property(
        property_type=entity_pb2.Property.PropertyType.NAME,
        name=entity_pb2.NameProperty(
            name=name,
            static_block=entity_pb2.NameProperty.StaticBlock.STATIC,
        ),
    )


def _transform_component(placement: EntityPlacement) -> entity_pb2.Component:
    position = placement.position
    rotation = placement.rotation
    scale = placement.scale
    return entity_pb2.Component(
        component_type=entity_pb2.Component.ComponentType.TRANSFORM,
        transform=entity_pb2.TransformComponent(
            position=_vec3_message(entity_pb2.Position, position),
            rotation=_vec3_message(entity_pb2.Rotation, rotation),
            scale=_vec3_message(entity_pb2.Scale, scale),
            field_501=_TRANSFORM_FIELD_501,
        ),
    )


def _vec3_message(message_type: type, vec: Vec3):
    return message_type(x=vec.x, y=vec.y, z=vec.z)
