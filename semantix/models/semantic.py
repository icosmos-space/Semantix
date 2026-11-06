from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from semantix.models.base import Base, TimestampMixin, uuid_pk


class SemanticModel(Base, TimestampMixin):
    __tablename__ = "semantic_models"
    __table_args__ = (UniqueConstraint("project_id", "name", name="uq_semantic_model_project_name"),)

    id: Mapped[str] = uuid_pk()
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    table_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    columns_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    published_revision_id: Mapped[str | None] = mapped_column(String(36), nullable=True)


class Metric(Base, TimestampMixin):
    __tablename__ = "metrics"
    __table_args__ = (UniqueConstraint("project_id", "name", name="uq_metric_project_name"),)

    id: Mapped[str] = uuid_pk()
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    expression: Mapped[str] = mapped_column(Text, nullable=False)
    dimensions_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")


class GlossaryTerm(Base, TimestampMixin):
    __tablename__ = "glossary_terms"

    id: Mapped[str] = uuid_pk()
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    synonyms_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    definition: Mapped[str] = mapped_column(Text, nullable=False)


class MdlRevision(Base, TimestampMixin):
    __tablename__ = "mdl_revisions"

    id: Mapped[str] = uuid_pk()
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), index=True)
    yaml_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
