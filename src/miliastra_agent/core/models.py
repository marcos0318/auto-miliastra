from pydantic import BaseModel, Field


class Vec3(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class EntityPlacement(BaseModel):
    template_id: int
    name: str = ""
    position: Vec3 = Field(default_factory=Vec3)
    rotation: Vec3 = Field(default_factory=Vec3)
    scale: Vec3 = Field(default_factory=lambda: Vec3(x=1.0, y=1.0, z=1.0))
    entity_id: int | None = None


class GiFileHeader(BaseModel):
    file_size: int
    version: int
    head_magic: int
    file_type: int
    content_length: int

    @property
    def type_name(self) -> str:
        names = {1: "GIP", 2: "GIL", 3: "GIA", 4: "GIR"}
        return names.get(self.file_type, f"UNKNOWN({self.file_type})")
