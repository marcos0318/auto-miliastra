from pathlib import Path

from miliastra_agent.core.gi_file import read_header, read_payload
from miliastra_agent.core.models import EntityPlacement, Vec3
from miliastra_agent.core.proto_gen import gia_pb2
from miliastra_agent.generators.entities import generate_platform_course
from miliastra_agent.generators.gia_encode import EntityEncoder, encode_gia_payload
from miliastra_agent.parsers.entities import parse_gia_payload


def test_encode_gia_payload_roundtrip() -> None:
    placements = [
        EntityPlacement(
            template_id=20001869,
            name="Block_A",
            entity_id=1078000001,
            position=Vec3(x=1.0, y=2.5, z=-3.0),
            rotation=Vec3(x=0.0, y=90.0, z=0.0),
            scale=Vec3(x=2.0, y=2.0, z=2.0),
        ),
        EntityPlacement(
            template_id=20001869,
            name="Block_B",
            position=Vec3(x=4.0, y=0.0, z=0.0),
        ),
    ]

    payload = encode_gia_payload(placements, entity_id_start=1078000000)
    collection = gia_pb2.GIACollection()
    collection.ParseFromString(payload)

    assert len(collection.Assets) == 2
    first = collection.Assets[0]
    assert first.type == 3  # ENTITY
    assert first.name == "Block_A"
    assert first.meta.asset_id == 1078000001
    assert first.entity_data.template_id == 20001869
    assert first.entity_data.data.entity_id == 1078000001
    assert first.entity_data.data.template.template_id == 20001869
    assert first.entity_data.data.template.field_2 == 1

    transform = first.entity_data.data.components[0].transform
    assert transform.position.x == 1.0
    assert transform.position.y == 2.5
    assert transform.position.z == -3.0
    assert transform.rotation.y == 90.0
    assert transform.scale.x == 2.0
    assert transform.field_501 == 4294967295

    parsed = parse_gia_payload(payload)
    assert len(parsed) == 2
    assert parsed[0].name == "Block_A"
    assert parsed[0].entity_id == 1078000001
    assert parsed[0].template_id == 20001869
    assert parsed[0].position.x == 1.0
    assert parsed[0].rotation.y == 90.0
    assert parsed[0].scale.x == 2.0

    assert parsed[1].name == "Block_B"
    assert parsed[1].entity_id == 1078000000
    assert parsed[1].position.x == 4.0


def test_entity_encoder_auto_ids() -> None:
    encoder = EntityEncoder(entity_id_start=9000)
    payload = encoder.encode_payload(
        [
            EntityPlacement(template_id=1, name="A", position=Vec3()),
            EntityPlacement(template_id=1, name="B", position=Vec3(x=1.0)),
        ]
    )
    parsed = parse_gia_payload(payload)
    assert [p.entity_id for p in parsed] == [9000, 9001]


def test_generate_platform_course_writes_valid_gia(tmp_path: Path) -> None:
    out = tmp_path / "platforms.gia"
    generate_platform_course(
        count=3,
        template_id=20001869,
        output_path=out,
        spacing=2.0,
        rise=0.5,
        entity_id_start=1078000100,
    )

    header = read_header(out.read_bytes())
    assert header.type_name == "GIA"
    parsed = parse_gia_payload(read_payload(out))
    assert len(parsed) == 3
    assert parsed[0].name == "Platform_0"
    assert parsed[0].entity_id == 1078000100
    assert parsed[1].position.x == 2.0
    assert parsed[1].position.y == 0.5
    assert parsed[2].position.x == 4.0
    assert parsed[2].position.y == 1.0
