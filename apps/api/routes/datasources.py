from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from apps.api.deps import CurrentUser, SessionDep
from semantix.datasource.service import DataSourceService, assert_project_member

router = APIRouter(prefix="/projects/{project_id}/datasources", tags=["datasources"])


class DataSourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    type: str = "postgres"
    host: str
    port: int = 5432
    database: str
    username: str
    password: str
    read_only: bool = True


class DataSourceResponse(BaseModel):
    id: str
    project_id: str
    name: str
    type: str
    host: str
    port: int
    database: str
    username: str
    read_only: bool

    model_config = {"from_attributes": True}


@router.get("", response_model=list[DataSourceResponse])
async def list_datasources(project_id: str, session: SessionDep, user: CurrentUser):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    return await DataSourceService(session).list(project_id)


@router.post("", response_model=DataSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_datasource(
    project_id: str,
    body: DataSourceCreate,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    return await DataSourceService(session).create(project_id=project_id, **body.model_dump())


@router.get("/{datasource_id}", response_model=DataSourceResponse)
async def get_datasource(
    project_id: str,
    datasource_id: str,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    return await DataSourceService(session).get(project_id, datasource_id)


@router.post("/{datasource_id}/test")
async def test_datasource(
    project_id: str,
    datasource_id: str,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    return await DataSourceService(session).test_connection(project_id, datasource_id)


@router.get("/{datasource_id}/schema")
async def get_schema(
    project_id: str,
    datasource_id: str,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    return await DataSourceService(session).get_schema(project_id, datasource_id)


@router.post("/{datasource_id}/schema/sync")
async def sync_schema(
    project_id: str,
    datasource_id: str,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    return await DataSourceService(session).sync_schema(project_id, datasource_id)
