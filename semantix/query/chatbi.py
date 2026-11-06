import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from semantix.agent.planner import PlanStep, Planner
from semantix.capability.registry import CapabilityRegistry
from semantix.core.errors import AppError
from semantix.engines.fixture import FixtureEngineAdapter
from semantix.engines.wren.adapter import WrenAdapter
from semantix.models.chat import ChatMessage, ChatSession
from semantix.models.datasource import DataSource
from semantix.query.executor import QueryExecutor
from semantix.query.markdown import build_answer_markdown, rows_to_markdown_table


DEMO_ONLINE_RATE_ROWS = [
    {"project_id": "项目A", "online_rate": 0.92},
    {"project_id": "项目B", "online_rate": 0.81},
    {"project_id": "项目C", "online_rate": 0.74},
]

DEMO_LOWEST_DEVICES = [
    {"device_id": "tacey_005", "online_rate": 0.61},
    {"device_id": "tacey_002", "online_rate": 0.68},
    {"device_id": "tacey_008", "online_rate": 0.71},
    {"device_id": "tacey_003", "online_rate": 0.73},
    {"device_id": "tacey_001", "online_rate": 0.76},
]

DEMO_ALARMS: dict[str, list[dict[str, Any]]] = {
    "tacey_002": [
        {"alarm_id": "A-1001", "level": "critical", "message": "离线超时", "status": "open"},
        {"alarm_id": "A-1002", "level": "warning", "message": "温度偏高", "status": "ack"},
    ],
    "tacey_005": [
        {"alarm_id": "A-2001", "level": "critical", "message": "心跳丢失", "status": "open"},
    ],
    "tacey_008": [
        {"alarm_id": "A-3001", "level": "info", "message": "固件待升级", "status": "open"},
    ],
    "tacey_003": [],
    "tacey_001": [
        {"alarm_id": "A-4001", "level": "warning", "message": "磁盘使用率 > 85%", "status": "open"},
    ],
}


class ChatBIService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.fixture = FixtureEngineAdapter()
        self.wren = WrenAdapter()
        self.planner = Planner()

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

        if not question.strip():
            raise AppError("invalid_input", "question is required", status_code=400)

        published = [
            c for c in await CapabilityRegistry(self.session).list(project_id) if c.status == "published"
        ]
        steps = await self.planner.plan(question, published)

        if len(steps) > 1 or (steps and steps[0].kind == "functional"):
            return await self._ask_planned(
                project_id=project_id,
                session_id=session_id,
                user_id=user_id,
                question=question,
                steps=steps,
                use_demo_rows=use_demo_rows,
            )

        return await self._ask_semantic(
            project_id=project_id,
            session_id=session_id,
            user_id=user_id,
            question=question,
            datasource_id=datasource_id,
            use_demo_rows=use_demo_rows,
            scenario=(steps[0].input_template.get("scenario") if steps else None),
        )

    async def _ask_planned(
        self,
        *,
        project_id: str,
        session_id: str,
        user_id: str,
        question: str,
        steps: list[PlanStep],
        use_demo_rows: bool,
    ) -> ChatMessage:
        step_results: list[dict[str, Any]] = []
        parts: list[str] = ["## 混合查询计划", ""]
        for i, step in enumerate(steps):
            parts.append(f"### Step {i + 1}: {step.rationale or step.capability_name}")
            result = await self._run_step(
                project_id=project_id,
                user_id=user_id,
                step=step,
                prior=step_results,
                use_demo_rows=use_demo_rows,
            )
            step_results.append(result)
            if result.get("markdown"):
                parts.append(result["markdown"])
            parts.append("")

        content = "\n".join(parts)
        summary = {
            "status": "hybrid",
            "steps": [
                {
                    "capability_name": s.capability_name,
                    "capability_id": s.capability_id,
                    "kind": s.kind,
                    "depends_on": s.depends_on,
                    "rationale": s.rationale,
                }
                for s in steps
            ],
            "step_results": [
                {k: v for k, v in r.items() if k != "markdown"} for r in step_results
            ],
        }
        sqls = [r.get("sql") for r in step_results if r.get("sql")]
        assistant = ChatMessage(
            session_id=session_id,
            role="assistant",
            content_markdown=content,
            sql_text=sqls[0] if sqls else None,
            execution_summary_json=json.dumps(summary, ensure_ascii=False, default=str),
            result_json=json.dumps({"steps": step_results}, ensure_ascii=False, default=str),
        )
        self.session.add(assistant)
        await self.session.commit()
        await self.session.refresh(assistant)
        return assistant

    async def _run_step(
        self,
        *,
        project_id: str,
        user_id: str,
        step: PlanStep,
        prior: list[dict[str, Any]],
        use_demo_rows: bool,
    ) -> dict[str, Any]:
        if step.kind == "semantic_data":
            scenario = step.input_template.get("scenario")
            q = str(step.input_template.get("question") or "")
            if scenario == "lowest_online_devices" or ("最低" in q and "在线率" in q):
                columns = ["device_id", "online_rate"]
                rows = DEMO_LOWEST_DEVICES
                sql = (
                    "SELECT device_id, online_rate FROM device_online_rate_7d "
                    "ORDER BY online_rate ASC LIMIT 5"
                )
                md = build_answer_markdown(
                    intro="在线率最低的 5 台设备：",
                    columns=columns,
                    rows=rows,
                    sql=sql,
                    chart_category="device_id",
                    chart_value="online_rate",
                    chart_title="在线率最低设备",
                )
                return {
                    "kind": "semantic_data",
                    "columns": columns,
                    "rows": rows,
                    "sql": sql,
                    "markdown": md,
                    "device_ids": [r["device_id"] for r in rows],
                }
            # Fall through to normal semantic answer pieces
            msg_like = await self._semantic_payload(
                project_id=project_id,
                user_id=user_id,
                question=q,
                datasource_id=None,
                use_demo_rows=True,
                scenario=scenario,
            )
            return msg_like

        # functional
        device_ids: list[str] = []
        if "device_ids_from_step" in step.input_template:
            idx = int(step.input_template["device_ids_from_step"])
            device_ids = list(prior[idx].get("device_ids") or [])
            limit = int(step.input_template.get("limit") or len(device_ids))
            device_ids = device_ids[:limit]
        elif step.input_template.get("device_id"):
            device_ids = [str(step.input_template["device_id"])]

        alarm_rows: list[dict[str, Any]] = []
        for did in device_ids:
            if use_demo_rows or not step.capability_id:
                for a in DEMO_ALARMS.get(did, [{"alarm_id": "-", "level": "info", "message": "无告警", "status": "closed"}]):
                    alarm_rows.append({"device_id": did, **a})
            else:
                try:
                    from semantix.capability.executor import CapabilityExecutor

                    out = await CapabilityExecutor(self.session).execute(
                        project_id=project_id,
                        capability_id=step.capability_id,
                        input_data={"device_id": did},
                        actor_user_id=user_id,
                    )
                    data = out.get("upstream", {}).get("data") or out.get("data") or out
                    if isinstance(data, list):
                        for a in data:
                            alarm_rows.append({"device_id": did, **(a if isinstance(a, dict) else {"value": a})})
                    elif isinstance(data, dict):
                        items = data.get("alarms") or data.get("items") or [data]
                        for a in items:
                            alarm_rows.append({"device_id": did, **(a if isinstance(a, dict) else {"value": a})})
                except AppError:
                    for a in DEMO_ALARMS.get(did, []):
                        alarm_rows.append({"device_id": did, **a})

        columns = ["device_id", "alarm_id", "level", "message", "status"]
        md = (
            "设备告警：\n\n"
            + rows_to_markdown_table(columns, alarm_rows)
            + f"\n\n_via `{step.capability_name or 'get_device_alarms'}`_"
        )
        return {
            "kind": "functional",
            "columns": columns,
            "rows": alarm_rows,
            "markdown": md,
            "device_ids": device_ids,
        }

    async def _semantic_payload(
        self,
        *,
        project_id: str,
        user_id: str,
        question: str,
        datasource_id: str | None,
        use_demo_rows: bool,
        scenario: str | None,
    ) -> dict[str, Any]:
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
        if use_demo_rows or not datasource_id:
            if scenario == "online_rate" or "在线率" in question:
                columns = ["project_id", "online_rate"]
                rows = DEMO_ONLINE_RATE_ROWS
            else:
                columns, rows = [], []
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
        return {
            "kind": "semantic_data",
            "columns": columns,
            "rows": rows,
            "sql": engine_sql.sql,
            "markdown": content,
        }

    async def _ask_semantic(
        self,
        *,
        project_id: str,
        session_id: str,
        user_id: str,
        question: str,
        datasource_id: str | None,
        use_demo_rows: bool,
        scenario: str | None,
    ) -> ChatMessage:
        payload = await self._semantic_payload(
            project_id=project_id,
            user_id=user_id,
            question=question,
            datasource_id=datasource_id,
            use_demo_rows=use_demo_rows,
            scenario=scenario,
        )
        summary = {
            "engine": "fixture",
            "sql": payload.get("sql"),
            "status": "demo_rows" if payload.get("rows") else "sql_only",
        }
        assistant = ChatMessage(
            session_id=session_id,
            role="assistant",
            content_markdown=payload["markdown"],
            sql_text=payload.get("sql"),
            execution_summary_json=json.dumps(summary, ensure_ascii=False),
            result_json=json.dumps(
                {"columns": payload.get("columns", []), "rows": payload.get("rows", [])},
                ensure_ascii=False,
                default=str,
            ),
        )
        self.session.add(assistant)
        await self.session.commit()
        await self.session.refresh(assistant)
        return assistant
