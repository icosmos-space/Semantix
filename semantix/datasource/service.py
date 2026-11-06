import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from semantix.core.errors import AppError
from semantix.datasource.connectors.postgres import PostgresConnector
from semantix.models.datasource import DataSource
from semantix.models.project import Membership
from semantix.security.crypto import decrypt_secret, encrypt_secret


async def assert_project_member(session: AsyncSession, *, project_id: str, user_id: str) -> None:
    membership = await session.scalar(
        select(Membership).where(
            Membership.project_id == project_id,
            Membership.user_id == user_id,
        )
    )
    if membership is None:
        raise AppError("forbidden", "Not a member of this project", status_code=403)


def _connector_for(ds: DataSource) -> PostgresConnector:
    if ds.type != "postgres":
        raise AppError("unsupported_datasource", f"Unsupported type: {ds.type}", status_code=400)
    return PostgresConnector(
        host=ds.host,
        port=ds.port,
        database=ds.database,
        username=ds.username,
        password=decrypt_secret(ds.password_encrypted),
    )


class DataSourceService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, project_id: str) -> list[DataSource]:
        result = await self.session.scalars(
            select(DataSource)
            .where(DataSource.project_id == project_id)
            .order_by(DataSource.created_at.desc())
        )
        return list(result.all())

    async def get(self, project_id: str, datasource_id: str) -> DataSource:
        ds = await self.session.scalar(
            select(DataSource).where(
                DataSource.id == datasource_id,
                DataSource.project_id == project_id,
            )
        )
        if ds is None:
            raise AppError("not_found", "Datasource not found", status_code=404)
        return ds

    async def create(
        self,
        *,
        project_id: str,
        name: str,
        type: str,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        read_only: bool = True,
    ) -> DataSource:
        ds = DataSource(
            project_id=project_id,
            name=name,
            type=type,
            host=host,
            port=port,
            database=database,
            username=username,
            password_encrypted=encrypt_secret(password),
            read_only=read_only,
        )
        self.session.add(ds)
        await self.session.commit()
        await self.session.refresh(ds)
        return ds

    async def test_connection(self, project_id: str, datasource_id: str) -> dict[str, str]:
        ds = await self.get(project_id, datasource_id)
        try:
            await _connector_for(ds).test_connection()
        except Exception as exc:
            raise AppError(
                "connection_failed",
                "Datasource connection failed",
                status_code=400,
                details={"error": str(exc)},
            ) from exc
        return {"status": "ok"}

    async def sync_schema(self, project_id: str, datasource_id: str) -> dict[str, Any]:
        ds = await self.get(project_id, datasource_id)
        try:
            schema = await _connector_for(ds).discover_schema()
        except Exception as exc:
            raise AppError(
                "schema_discovery_failed",
                "Schema discovery failed",
                status_code=400,
                details={"error": str(exc)},
            ) from exc
        ds.schema_cache_json = json.dumps(schema)
        await self.session.commit()
        return schema

    async def get_schema(self, project_id: str, datasource_id: str) -> dict[str, Any]:
        ds = await self.get(project_id, datasource_id)
        if not ds.schema_cache_json:
            return await self.sync_schema(project_id, datasource_id)
        return json.loads(ds.schema_cache_json)
