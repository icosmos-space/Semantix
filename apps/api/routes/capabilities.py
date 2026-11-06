from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from apps.api.deps import CurrentUser, SessionDep
from semantix.capability.discovery import CapabilityDiscovery
from semantix.capability.executor import CapabilityExecutor
from semantix.capability.registry import CapabilityRegistry
from semantix.capability.schemas import CapabilityCreate, CapabilityOut
from semantix.datasource.service import assert_project_member

router = APIRouter(prefix="/projects/{project_id}/capabilities", tags=["capabilities"])


class ExecuteBody(BaseModel):
    input: dict = Field(default_factory=dict)


@router.get("", response_model=list[CapabilityOut])
async def list_capabilities(
    project_id: str,
    session: SessionDep,
    user: CurrentUser,
    kind: str | None = None,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    return await CapabilityRegistry(session).list(project_id, kind=kind)


@router.get("/search", response_model=list[CapabilityOut])
async def search_capabilities(
    project_id: str,
    q: str,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    return await CapabilityDiscovery(session).search(project_id, q)


@router.post("", response_model=CapabilityOut, status_code=status.HTTP_201_CREATED)
async def create_capability(
    project_id: str,
    body: CapabilityCreate,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    return await CapabilityRegistry(session).register(
        project_id=project_id,
        name=body.name,
        kind=body.kind,
        description=body.description,
        source=body.source,
        source_ref=body.source_ref,
        input_schema=body.input_schema,
        output_schema=body.output_schema,
        config=body.config,
    )


@router.post("/{capability_id}/publish", response_model=CapabilityOut)
async def publish_capability(
    project_id: str,
    capability_id: str,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    return await CapabilityRegistry(session).publish(project_id, capability_id)


@router.post("/{capability_id}/execute")
async def execute_capability(
    project_id: str,
    capability_id: str,
    body: ExecuteBody,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    return await CapabilityExecutor(session).execute(
        project_id=project_id,
        capability_id=capability_id,
        input_data=body.input,
        actor_user_id=user.id,
    )
