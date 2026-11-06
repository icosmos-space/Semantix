from fastapi import APIRouter
from pydantic import BaseModel, Field

from apps.api.deps import CurrentUser, SessionDep
from semantix.datasource.service import assert_project_member
from semantix.query.executor import QueryExecutor

router = APIRouter(prefix="/projects/{project_id}/query", tags=["query"])


class ExecuteRequest(BaseModel):
    datasource_id: str
    sql: str = Field(min_length=1)
    max_rows: int = Field(default=1000, ge=1, le=10000)


@router.post("/execute")
async def execute_sql(
    project_id: str,
    body: ExecuteRequest,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    result = await QueryExecutor(session).execute(
        project_id=project_id,
        datasource_id=body.datasource_id,
        sql=body.sql,
        actor_user_id=user.id,
        max_rows=body.max_rows,
    )
    return {
        "columns": result.columns,
        "rows": result.rows,
        "sql": result.sql,
        "query_run_id": result.query_run_id,
        "truncated": result.truncated,
        "duration_ms": result.duration_ms,
        "execution_summary": result.execution_summary,
    }
