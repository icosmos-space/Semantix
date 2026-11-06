import json

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from apps.api.deps import CurrentUser, SessionDep
from semantix.datasource.service import assert_project_member
from semantix.query.chatbi import ChatBIService

router = APIRouter(prefix="/projects/{project_id}/chatbi", tags=["chatbi"])


class SessionCreate(BaseModel):
    title: str = "New chat"


class SessionResponse(BaseModel):
    id: str
    title: str

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    content: str = Field(min_length=1)
    datasource_id: str | None = None
    use_demo_rows: bool = True


class MessageResponse(BaseModel):
    id: str
    role: str
    content_markdown: str
    sql: str | None = None
    columns: list[str] = []
    rows: list[dict] = []
    execution_summary: dict = {}


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    project_id: str,
    body: SessionCreate,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    s = await ChatBIService(session).create_session(
        project_id=project_id, user_id=user.id, title=body.title
    )
    return s


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(project_id: str, session: SessionDep, user: CurrentUser):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    return await ChatBIService(session).list_sessions(project_id=project_id, user_id=user.id)


@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    project_id: str,
    session_id: str,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    svc = ChatBIService(session)
    await svc.get_session(project_id=project_id, session_id=session_id, user_id=user.id)
    messages = await svc.list_messages(session_id)
    out: list[MessageResponse] = []
    for m in messages:
        result = json.loads(m.result_json) if m.result_json else {}
        summary = json.loads(m.execution_summary_json) if m.execution_summary_json else {}
        out.append(
            MessageResponse(
                id=m.id,
                role=m.role,
                content_markdown=m.content_markdown,
                sql=m.sql_text,
                columns=result.get("columns", []),
                rows=result.get("rows", []),
                execution_summary=summary,
            )
        )
    return out


@router.post(
    "/sessions/{session_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_message(
    project_id: str,
    session_id: str,
    body: MessageCreate,
    session: SessionDep,
    user: CurrentUser,
):
    await assert_project_member(session, project_id=project_id, user_id=user.id)
    msg = await ChatBIService(session).ask(
        project_id=project_id,
        session_id=session_id,
        user_id=user.id,
        question=body.content,
        datasource_id=body.datasource_id,
        use_demo_rows=body.use_demo_rows,
    )
    result = json.loads(msg.result_json) if msg.result_json else {}
    summary = json.loads(msg.execution_summary_json) if msg.execution_summary_json else {}
    return MessageResponse(
        id=msg.id,
        role=msg.role,
        content_markdown=msg.content_markdown,
        sql=msg.sql_text,
        columns=result.get("columns", []),
        rows=result.get("rows", []),
        execution_summary=summary,
    )
