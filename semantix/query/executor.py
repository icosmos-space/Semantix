import time
from dataclasses import dataclass, field
from typing import Any

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession

from semantix.core.errors import AppError
from semantix.datasource.service import DataSourceService
from semantix.engines.sqlglot_policy import SqlPolicyError, assert_readonly_sql
from semantix.models.audit import QueryRun
from semantix.security.crypto import decrypt_secret


@dataclass
class QueryResult:
    columns: list[str]
    rows: list[dict[str, Any]]
    sql: str
    query_run_id: str
    truncated: bool = False
    duration_ms: float = 0.0
    execution_summary: dict[str, Any] = field(default_factory=dict)


class QueryExecutor:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(
        self,
        *,
        project_id: str,
        datasource_id: str,
        sql: str,
        actor_user_id: str | None,
        engine: str = "direct",
        timeout_s: float = 30.0,
        max_rows: int = 1000,
    ) -> QueryResult:
        try:
            safe_sql = assert_readonly_sql(sql)
        except SqlPolicyError as exc:
            raise AppError("sql_policy_violation", str(exc), status_code=400) from exc

        ds = await DataSourceService(self.session).get(project_id, datasource_id)
        password = decrypt_secret(ds.password_encrypted)

        started = time.perf_counter()
        run = QueryRun(
            project_id=project_id,
            datasource_id=datasource_id,
            actor_user_id=actor_user_id,
            engine=engine,
            sql_text=safe_sql,
            status="running",
        )
        self.session.add(run)
        await self.session.flush()

        try:
            conn = await asyncpg.connect(
                host=ds.host,
                port=ds.port,
                user=ds.username,
                password=password,
                database=ds.database,
                timeout=timeout_s,
                command_timeout=timeout_s,
            )
            try:
                limited_sql = f"SELECT * FROM ({safe_sql}) AS _semantix_q LIMIT {max_rows + 1}"
                records = await conn.fetch(limited_sql)
            finally:
                await conn.close()

            truncated = len(records) > max_rows
            records = records[:max_rows]
            columns = list(records[0].keys()) if records else []
            rows = [dict(r) for r in records]
            duration_ms = (time.perf_counter() - started) * 1000
            run.status = "ok"
            run.row_count = len(rows)
            run.duration_ms = duration_ms
            await self.session.commit()
            return QueryResult(
                columns=columns,
                rows=rows,
                sql=safe_sql,
                query_run_id=run.id,
                truncated=truncated,
                duration_ms=duration_ms,
                execution_summary={
                    "engine": engine,
                    "datasource_id": datasource_id,
                    "row_count": len(rows),
                    "truncated": truncated,
                    "duration_ms": duration_ms,
                    "status": "ok",
                },
            )
        except Exception as exc:
            duration_ms = (time.perf_counter() - started) * 1000
            run.status = "error"
            run.duration_ms = duration_ms
            run.error_message = str(exc)
            await self.session.commit()
            raise AppError(
                "query_failed",
                "Query execution failed",
                status_code=400,
                details={"error": str(exc), "query_run_id": run.id},
            ) from exc
