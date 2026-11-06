import json

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from apps.api.deps import CurrentUser, SessionDep
from semantix.datasource.service import assert_project_member
from semantix.semantic.models_service import SemanticService

router = APIRouter(prefix="/projects/{project_id}/semantic", tags=["semantic"])


class ModelCreate(BaseModel):
    name: str
    table_name: str
    description: str | None = None
    columns: list[dict] = Field(default_factory=list)


class ModelResponse(BaseModel):
    id: str
    name: str
    table_name: str
    description: str | None
    columns: list[dict]
    published_revision_id: str | None

    model_config = {"from_attributes": True}


class MetricCreate(BaseModel):
    name: str
    model_name: str
    expression: str
    dimensions: list[str] = Field(default_factory=list)
    description: str | None = None


class MetricResponse(BaseModel):
    id: str
    name: str
    model_name: str
    expression: str
    dimensions: list[str]
    description: str | None
    status: str


class MdlCreate(BaseModel):
    yaml_text: str
    note: str | None = None


class MdlResponse(BaseModel):
    id: str
    status: str
    note: str | None
    yaml_text: str


@router.get("/models", response_model=list[ModelResponse])
async def list_models(project_id: str, session: SessionDep, user: CurrentUser):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    models = await SemanticService(session).list_models(project_id)
    return [
        ModelResponse(
            id=m.id,
            name=m.name,
            table_name=m.table_name,
            description=m.description,
            columns=json.loads(m.columns_json or "[]"),
            published_revision_id=m.published_revision_id,
        )
        for m in models
    ]


@router.post("/models", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(project_id: str, body: ModelCreate, session: SessionDep, user: CurrentUser):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    m = await SemanticService(session).create_model(project_id=project_id, **body.model_dump())
    return ModelResponse(
        id=m.id,
        name=m.name,
        table_name=m.table_name,
        description=m.description,
        columns=json.loads(m.columns_json or "[]"),
        published_revision_id=m.published_revision_id,
    )


@router.get("/metrics", response_model=list[MetricResponse])
async def list_metrics(project_id: str, session: SessionDep, user: CurrentUser):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    metrics = await SemanticService(session).list_metrics(project_id)
    return [
        MetricResponse(
            id=m.id,
            name=m.name,
            model_name=m.model_name,
            expression=m.expression,
            dimensions=json.loads(m.dimensions_json or "[]"),
            description=m.description,
            status=m.status,
        )
        for m in metrics
    ]


@router.post("/metrics", response_model=MetricResponse, status_code=status.HTTP_201_CREATED)
async def create_metric(project_id: str, body: MetricCreate, session: SessionDep, user: CurrentUser):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    m = await SemanticService(session).create_metric(project_id=project_id, **body.model_dump())
    return MetricResponse(
        id=m.id,
        name=m.name,
        model_name=m.model_name,
        expression=m.expression,
        dimensions=json.loads(m.dimensions_json or "[]"),
        description=m.description,
        status=m.status,
    )


@router.get("/mdl/revisions", response_model=list[MdlResponse])
async def list_mdl(project_id: str, session: SessionDep, user: CurrentUser):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    revs = await SemanticService(session).list_revisions(project_id)
    return [MdlResponse(id=r.id, status=r.status, note=r.note, yaml_text=r.yaml_text) for r in revs]


@router.post("/mdl/revisions", response_model=MdlResponse, status_code=status.HTTP_201_CREATED)
async def create_mdl(project_id: str, body: MdlCreate, session: SessionDep, user: CurrentUser):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    r = await SemanticService(session).create_mdl_revision(
        project_id=project_id, yaml_text=body.yaml_text, note=body.note
    )
    return MdlResponse(id=r.id, status=r.status, note=r.note, yaml_text=r.yaml_text)


@router.post("/mdl/revisions/{revision_id}/publish", response_model=MdlResponse)
async def publish_mdl(project_id: str, revision_id: str, session: SessionDep, user: CurrentUser):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    r = await SemanticService(session).publish_mdl_revision(project_id=project_id, revision_id=revision_id)
    return MdlResponse(id=r.id, status=r.status, note=r.note, yaml_text=r.yaml_text)
