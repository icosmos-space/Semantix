import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from semantix.core.errors import AppError
from semantix.engines.fixture import FixtureEngineAdapter
from semantix.engines.wren.adapter import WrenAdapter
from semantix.models.chat import ChatMessage, ChatSession
from semantix.models.datasource import DataSource
from semantix.query.executor import QueryExecutor
from semantix.query.markdown import build_answer_markdown


DEMO_ONLINE_RATE_ROWS = [
    {"project_id": "项目A", "online_rate": 0.92},
    {"project_id": "项目B", "online_rate": 0.81},
    {"project_id": "项目C", "online_rate": 0.74},
]


class ChatBIService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.fixture = FixtureEngineAdapter()
        self.wren = WrenAdapter()

    async def create_session(self, *, project_id: str, user_id: str, title: str = "New chat") -> ChatSession:
        session = ChatSession(project_id=project_id, user_id=user_id, title=title)
        self.session.add(session)
        await self.session.commit()
        await self.session.refresh(session)
        return session

    async def list_sessions(self, *, project_id: str, user_id: str) -> list[ChatSession]:
        result = await self.session.scalars(
            select(ChatSession)
            .where(ChatSession.project_id == project_id, ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
        )
        return list(result.all())

    async def get_session(self, *, project_id: str, session_id: str, user_id: str) -> ChatSession:
        session = await self.session.scalar(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.project_id == project_id,
                ChatSession.user_id == user_id,
            )
        )
        if session is None:
            raise AppError("not_found", "Chat session not found", status_code=404)
        return session

    async def list_messages(self, session_id: str) -> list[ChatMessage]:
        result = await self.session.scalars(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        return list(result.all())

    async def ask(
        self,
        *,
        project_id: str,
        session_id: str,
        user_id: str,
        question: str,
        datasource_id: str | None = None,
        use_demo_rows: bool = False,
    ) -> ChatMessage:
        await self.get_session(project_id=project_id, session_id=session_id, user_id=user_id)

        user_msg = ChatMessage(
            session_id=session_id,
            role="user",
            content_markdown=question,
        )
        self.session.add(user_msg)

        context: dict[str, Any] = {"project_id": project_id}
        try:
            engine_sql = await self.wren.generate_sql(question, context)
        except NotImplementedError:
            try:
                engine_sql = await self.fixture.generate_sql(question, context)
            except NotImplementedError as exc:
                raise AppError("unsupported_question", str(exc), status_code=400) from exc

        columns: list[str] = []
        rows: list[dict[str, Any]] = []
        summary: dict[str, Any] = {
            "engine": engine_sql.engine,
            "sql": engine_sql.sql,
            "rationale": engine_sql.rationale,
            "status": "planned",
        }

        if use_demo_rows or not datasource_id:
            if "在线率" in question:
                columns = ["project_id", "online_rate"]
                rows = DEMO_ONLINE_RATE_ROWS
                summary["status"] = "demo_rows"
            else:
                columns = []
                rows = []
                summary["status"] = "sql_only"
        else:
            ds = await self.session.scalar(
                select(DataSource).where(
                    DataSource.id == datasource_id,
                    DataSource.project_id == project_id,
                )
            )
            if ds is None:
                raise AppError("not_found", "Datasource not found", status_code=404)
            result = await QueryExecutor(self.session).execute(
                project_id=project_id,
                datasource_id=datasource_id,
                sql=engine_sql.sql,
                actor_user_id=user_id,
                engine=engine_sql.engine,
            )
            columns = result.columns
            rows = result.rows
            summary = result.execution_summary
            summary["engine"] = engine_sql.engine
            summary["rationale"] = engine_sql.rationale

        chart_category = "project_id" if "project_id" in columns else None
        chart_value = "online_rate" if "online_rate" in columns else None
        content = build_answer_markdown(
            intro="查询结果如下：",
            columns=columns,
            rows=rows,
            sql=engine_sql.sql,
            chart_category=chart_category,
            chart_value=chart_value,
            chart_title="近7天设备在线率" if chart_value else None,
        )

        assistant = ChatMessage(
            session_id=session_id,
            role="assistant",
            content_markdown=content,
            sql_text=engine_sql.sql,
            execution_summary_json=json.dumps(summary, ensure_ascii=False),
            result_json=json.dumps({"columns": columns, "rows": rows}, ensure_ascii=False, default=str),
        )
        self.session.add(assistant)
        await self.session.commit()
        await self.session.refresh(assistant)
        return assistant
