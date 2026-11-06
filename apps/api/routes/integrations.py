import json

from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from apps.api.deps import CurrentUser, SessionDep
from semantix.datasource.service import assert_project_member
from semantix.integrations.openapi.import_service import OpenApiImportService
from semantix.models.integration import Integration, ToolSemanticOverlay

router = APIRouter(prefix="/projects/{project_id}/integrations", tags=["integrations"])


class IntegrationCreate(BaseModel):
    name: str
    base_url: str
    auth_type: str = "none"
    auth_token: str | None = None


class IntegrationOut(BaseModel):
    id: str
    name: str
    base_url: str
    auth_type: str

    model_config = {"from_attributes": True}


class ImportBody(BaseModel):
    openapi: dict


class OverlayUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    intents: list[str] | None = None
    entities: list[str] | None = None
    read_only_confirmed: bool | None = None


class OverlayOut(BaseModel):
    id: str
    operation_id: str
    name: str
    description: str
    method: str
    path: str
    read_only_confirmed: bool
    capability_id: str | None
    intents: list[str] = Field(default_factory=list)


@router.get("", response_model=list[IntegrationOut])
async def list_integrations(project_id: str, session: SessionDep, user: CurrentUser):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    result = await session.scalars(
        select(Integration).where(Integration.project_id == project_id).order_by(Integration.name)
    )
    return list(result.all())


@router.post("", response_model=IntegrationOut, status_code=status.HTTP_201_CREATED)
async def create_integration(
    project_id: str,
    body: IntegrationCreate,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    return await OpenApiImportService(session).create_integration(
        project_id=project_id,
        name=body.name,
        base_url=body.base_url,
        auth_type=body.auth_type,
        auth_token=body.auth_token,
    )


@router.post("/{integration_id}/import")
async def import_openapi(
    project_id: str,
    integration_id: str,
    body: ImportBody,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    return await OpenApiImportService(session).import_spec(
        project_id=project_id,
        integration_id=integration_id,
        spec=body.openapi,
    )


@router.get("/{integration_id}/overlays", response_model=list[OverlayOut])
async def list_overlays(
    project_id: str,
    integration_id: str,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    integration = await session.scalar(
        select(Integration).where(Integration.id == integration_id, Integration.project_id == project_id)
    )
    if integration is None:
        from semantix.core.errors import AppError

        raise AppError("not_found", "Integration not found", status_code=404)
    result = await session.scalars(
        select(ToolSemanticOverlay).where(ToolSemanticOverlay.integration_id == integration_id)
    )
    out = []
    for o in result.all():
        out.append(
            OverlayOut(
                id=o.id,
                operation_id=o.operation_id,
                name=o.name,
                description=o.description,
                method=o.method,
                path=o.path,
                read_only_confirmed=o.read_only_confirmed,
                capability_id=o.capability_id,
                intents=json.loads(o.intents_json or "[]"),
            )
        )
    return out


@router.patch("/overlays/{overlay_id}", response_model=OverlayOut)
async def patch_overlay(
    project_id: str,
    overlay_id: str,
    body: OverlayUpdate,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    o = await OpenApiImportService(session).update_overlay(
        project_id=project_id,
        overlay_id=overlay_id,
        **body.model_dump(exclude_unset=True),
    )
    return OverlayOut(
        id=o.id,
        operation_id=o.operation_id,
        name=o.name,
        description=o.description,
        method=o.method,
        path=o.path,
        read_only_confirmed=o.read_only_confirmed,
        capability_id=o.capability_id,
        intents=json.loads(o.intents_json or "[]"),
    )


@router.post("/overlays/{overlay_id}/publish")
async def publish_overlay(
    project_id: str,
    overlay_id: str,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    return await OpenApiImportService(session).publish_overlay_capability(
        project_id=project_id,
        overlay_id=overlay_id,
    )
