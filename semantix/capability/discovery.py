from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from semantix.models.capability import Capability


class CapabilityDiscovery:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search(self, project_id: str, query: str) -> list[Capability]:
        q = f"%{query.strip()}%"
        result = await self.session.scalars(
            select(Capability).where(
                Capability.project_id == project_id,
                Capability.status == "published",
                or_(Capability.name.ilike(q), Capability.description.ilike(q)),
            )
        )
        return list(result.all())
