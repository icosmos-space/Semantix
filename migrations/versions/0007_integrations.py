"""integrations openapi

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-06

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "integrations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("base_url", sa.String(500), nullable=False),
        sa.Column("auth_type", sa.String(32), nullable=False),
        sa.Column("auth_token_encrypted", sa.Text(), nullable=True),
        sa.Column("allowed_hosts", sa.String(1000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("project_id", "name", name="uq_integration_project_name"),
    )
    op.create_index("ix_integrations_project_id", "integrations", ["project_id"])

    op.create_table(
        "raw_openapi_specs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("integration_id", sa.String(36), sa.ForeignKey("integrations.id"), nullable=False),
        sa.Column("version_label", sa.String(120), nullable=False),
        sa.Column("spec_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_raw_openapi_specs_integration_id", "raw_openapi_specs", ["integration_id"])

    op.create_table(
        "tool_semantic_overlays",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("integration_id", sa.String(36), sa.ForeignKey("integrations.id"), nullable=False),
        sa.Column("operation_id", sa.String(200), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("intents_json", sa.Text(), nullable=False),
        sa.Column("entities_json", sa.Text(), nullable=False),
        sa.Column("read_only_confirmed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("method", sa.String(16), nullable=False),
        sa.Column("path", sa.String(500), nullable=False),
        sa.Column("capability_id", sa.String(36), sa.ForeignKey("capabilities.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("integration_id", "operation_id", name="uq_overlay_integration_operation"),
    )
    op.create_index("ix_tool_semantic_overlays_integration_id", "tool_semantic_overlays", ["integration_id"])


def downgrade() -> None:
    op.drop_table("tool_semantic_overlays")
    op.drop_table("raw_openapi_specs")
    op.drop_table("integrations")
