from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from semantix.models.base import Base, TimestampMixin, uuid_pk


class Capability(Base, TimestampMixin):
    __tablename__ = "capabilities"
    __table_args__ = (UniqueConstraint("project_id", "name", name="uq_capability_project_name"),)

    id: Mapped[str] = uuid_pk()
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)  # semantic_data|functional|knowledge
    operation: Mapped[str] = mapped_column(String(16), nullable=False, default="read")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="system")
    source_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    input_schema_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    output_schema_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    config_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
