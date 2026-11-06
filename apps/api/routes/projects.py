from fastapi import APIRouter, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from apps.api.deps import CurrentUser, SessionDep
from apps.api.schemas import ProjectCreate, ProjectResponse
from semantix.core.errors import AppError
from semantix.models.project import ROLE_OWNER, Membership, Project

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
async def list_projects(session: SessionDep, user: CurrentUser) -> list[Project]:
    result = await session.scalars(
        select(Project)
        .join(Membership, Membership.project_id == Project.id)
        .where(Membership.user_id == user.id)
        .order_by(Project.created_at.desc())
    )
    return list(result.all())


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    body: ProjectCreate,
    session: SessionDep,
    user: CurrentUser,
) -> Project:
    existing = await session.scalar(select(Project).where(Project.slug == body.slug))
    if existing is not None:
        raise AppError("slug_taken", "Project slug already exists", status_code=409)
    project = Project(name=body.name, slug=body.slug)
    session.add(project)
    await session.flush()
    membership = Membership(user_id=user.id, project_id=project.id, role=ROLE_OWNER)
    session.add(membership)
    await session.commit()
    await session.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, session: SessionDep, user: CurrentUser) -> Project:
    project = await session.scalar(
        select(Project)
        .options(selectinload(Project.memberships))
        .where(Project.id == project_id)
    )
    if project is None:
        raise AppError("not_found", "Project not found", status_code=404)
    if not any(m.user_id == user.id for m in project.memberships):
        raise AppError("forbidden", "Not a member of this project", status_code=403)
    return project
