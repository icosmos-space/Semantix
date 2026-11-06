import json

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from semantix.core.errors import AppError
from semantix.models.capability import Capability


class CapabilityRegistry:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register(
        self,
        *,
        project_id: str,
        name: str,
        kind: str,
        description: str | None = None,
        source: str = "system",
        source_ref: str | None = None,
        input_schema: dict | None = None,
        output_schema: dict | None = None,
        config: dict | None = None,
        status: str = "draft",
    ) -> Capability:
        existing = await self.session.scalar(
            select(Capability).where(Capability.project_id == project_id, Capability.name == name)
        )
        if existing:
            raise AppError("capability_exists", "Capability already exists", status_code=409)
        cap = Capability(
            project_id=project_id,
            name=name,
            kind=kind,
            operation="read",
            status=status,
            description=description,
            source=source,
            source_ref=source_ref,
            input_schema_json=json.dumps(input_schema or {}),
            output_schema_json=json.dumps(output_schema or {}),
            config_json=json.dumps(config or {}),
        )
        self.session.add(cap)
        await self.session.commit()
        await self.session.refresh(cap)
        return cap

    async def list(self, project_id: str, *, kind: str | None = None) -> list[Capability]:
        stmt = select(Capability).where(Capability.project_id == project_id)
        if kind:
            stmt = stmt.where(Capability.kind == kind)
        result = await self.session.scalars(stmt.order_by(Capability.name))
        return list(result.all())

    async def get(self, project_id: str, capability_id: str) -> Capability:
        cap = await self.session.scalar(
            select(Capability).where(Capability.id == capability_id, Capability.project_id == project_id)
        )
        if cap is None:
            raise AppError("not_found", "Capability not found", status_code=404)
        return cap

    async def publish(self, project_id: str, capability_id: str) -> Capability:
        cap = await self.get(project_id, capability_id)
        if cap.operation != "read":
            raise AppError("not_readonly", "Only read capabilities can be published", status_code=400)
        cap.status = "published"
        await self.session.commit()
        await self.session.refresh(cap)
        return cap
