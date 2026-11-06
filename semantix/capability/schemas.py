from pydantic import BaseModel, Field


class CapabilityCreate(BaseModel):
    name: str
    kind: str = Field(pattern="^(semantic_data|functional|knowledge)$")
    description: str | None = None
    source: str = "system"
    source_ref: str | None = None
    input_schema: dict = Field(default_factory=dict)
    output_schema: dict = Field(default_factory=dict)
    config: dict = Field(default_factory=dict)


class CapabilityOut(BaseModel):
    id: str
    name: str
    kind: str
    operation: str
    status: str
    description: str | None
    source: str
    source_ref: str | None

    model_config = {"from_attributes": True}
