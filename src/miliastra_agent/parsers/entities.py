"""Extract entity placements from GIL/GIA protobuf payloads."""

from __future__ import annotations

from miliastra_agent.core.models import EntityPlacement, Vec3
from miliastra_agent.core.proto_gen import gia_pb2
from miliastra_agent.core.proto_gen.asset_pb2 import Asset
from miliastra_agent.core.proto_gen.entity_pb2 import Component, Property
from miliastra_agent.core.wire import get_bytes_fields, get_string, get_varint


def parse_gia_payload(payload: bytes) -> list[EntityPlacement]:
    collection = gia_pb2.GIACollection()
    collection.ParseFromString(payload)
    placements: list[EntityPlacement] = []
    for asset in collection.Assets:
        if asset.type != Asset.AssetType.ENTITY or not asset.HasField("entity_data"):
            continue
        placements.append(_entity_from_gia_asset(asset))
    return placements


def parse_gil_payload(payload: bytes) -> list[EntityPlacement]:
    placements: list[EntityPlacement] = []
    level_name = get_string(payload, 2) or ""

    for chunk in get_bytes_fields(payload, 5):
        for item in get_bytes_fields(chunk, 1):
            placement = _entity_from_gil_logic(item)
            if placement is not None:
                if level_name and not placement.name:
                    placement.name = level_name
                placements.append(placement)

    for chunk in get_bytes_fields(payload, 27):
        for item in get_bytes_fields(chunk, 1):
            placement = _entity_from_gil_placement(item)
            if placement is not None:
                placements.append(placement)

    return placements


def parse_payload(payload: bytes, *, file_type: int) -> list[EntityPlacement]:
    if file_type == 2:
        return parse_gil_payload(payload)
    return parse_gia_payload(payload)


def _entity_from_gia_asset(asset: Asset) -> EntityPlacement:
    entity = asset.entity_data
    data = entity.data
    name = asset.name or _name_from_properties(data.properties) or f"Entity_{data.entity_id}"
    position, rotation, scale = _transform_from_components(data.components)
    return EntityPlacement(
        template_id=entity.template_id or data.template_id_ref,
        name=name,
        position=position,
        rotation=rotation,
        scale=scale,
        entity_id=data.entity_id,
    )


def _entity_from_gil_logic(data: bytes) -> EntityPlacement | None:
    entity_id = get_varint(data, 1)
    template_id = get_varint(data, 8)
    template_ref = get_bytes_fields(data, 2)
    if template_id is None and template_ref:
        template_id = get_varint(template_ref[0], 1)
    if entity_id is None or template_id is None:
        return None

    properties = [_parse_property(chunk) for chunk in get_bytes_fields(data, 5)]
    components = [_parse_component(chunk) for chunk in get_bytes_fields(data, 6)]
    name = _name_from_properties(properties) or f"Entity_{entity_id}"
    position, rotation, scale = _transform_from_components(components)
    return EntityPlacement(
        template_id=template_id,
        name=name,
        position=position,
        rotation=rotation,
        scale=scale,
        entity_id=entity_id,
    )


def _entity_from_gil_placement(data: bytes) -> EntityPlacement | None:
    entity_id = get_varint(data, 1)
    template_id = get_varint(data, 2)
    if entity_id is None or template_id is None:
        return None

    properties = [_parse_property(chunk) for chunk in get_bytes_fields(data, 4)]
    components = [_parse_component(chunk) for chunk in get_bytes_fields(data, 5)]
    name = _name_from_properties(properties) or f"Entity_{entity_id}"
    position, rotation, scale = _transform_from_components(components)
    return EntityPlacement(
        template_id=template_id,
        name=name,
        position=position,
        rotation=rotation,
        scale=scale,
        entity_id=entity_id,
    )


def _parse_property(data: bytes) -> Property:
    prop = Property()
    prop.ParseFromString(data)
    return prop


def _parse_component(data: bytes) -> Component:
    comp = Component()
    comp.ParseFromString(data)
    return comp


def _name_from_properties(properties: list[Property]) -> str:
    for prop in properties:
        if prop.property_type == Property.PropertyType.NAME and prop.HasField("name"):
            return prop.name.name
    return ""


def _transform_from_components(
    components: list[Component],
) -> tuple[Vec3, Vec3, Vec3]:
    position = Vec3()
    rotation = Vec3()
    scale = Vec3(x=1.0, y=1.0, z=1.0)

    for component in components:
        if component.component_type != Component.ComponentType.TRANSFORM:
            continue
        if not component.HasField("transform"):
            continue
        transform = component.transform
        if transform.HasField("position"):
            position = Vec3(
                x=transform.position.x,
                y=transform.position.y,
                z=transform.position.z,
            )
        if transform.HasField("rotation"):
            rotation = Vec3(
                x=transform.rotation.x,
                y=transform.rotation.y,
                z=transform.rotation.z,
            )
        if transform.HasField("scale"):
            scale = Vec3(
                x=transform.scale.x,
                y=transform.scale.y,
                z=transform.scale.z,
            )
        break

    return position, rotation, scale
