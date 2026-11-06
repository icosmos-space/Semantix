from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from semantix.models.base import Base, TimestampMixin, uuid_pk


class Integration(Base, TimestampMixin):
    __tablename__ = "integrations"
    __table_args__ = (UniqueConstraint("project_id", "name", name="uq_integration_project_name"),)

    id: Mapped[str] = uuid_pk()
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    auth_type: Mapped[str] = mapped_column(String(32), nullable=False, default="none")
    auth_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    allowed_hosts: Mapped[str] = mapped_column(String(1000), nullable=False, default="")


class RawOpenApiSpec(Base, TimestampMixin):
    __tablename__ = "raw_openapi_specs"

    id: Mapped[str] = uuid_pk()
    integration_id: Mapped[str] = mapped_column(String(36), ForeignKey("integrations.id"), index=True)
    version_label: Mapped[str] = mapped_column(String(120), nullable=False, default="imported")
    spec_json: Mapped[str] = mapped_column(Text, nullable=False)


class ToolSemanticOverlay(Base, TimestampMixin):
    __tablename__ = "tool_semantic_overlays"
    __table_args__ = (
        UniqueConstraint("integration_id", "operation_id", name="uq_overlay_integration_operation"),
    )

    id: Mapped[str] = uuid_pk()
    integration_id: Mapped[str] = mapped_column(String(36), ForeignKey("integrations.id"), index=True)
    operation_id: Mapped[str] = mapped_column(String(200), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    intents_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    entities_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    read_only_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    method: Mapped[str] = mapped_column(String(16), nullable=False, default="GET")
    path: Mapped[str] = mapped_column(String(500), nullable=False, default="/")
    capability_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("capabilities.id"), nullable=True)
