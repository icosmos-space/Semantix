import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from semantix.capability.registry import CapabilityRegistry
from semantix.core.errors import AppError
from semantix.query.chatbi import ChatBIService


class CapabilityExecutor:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.registry = CapabilityRegistry(session)

    async def execute(
        self,
        *,
        project_id: str,
        capability_id: str,
        input_data: dict[str, Any],
        actor_user_id: str,
    ) -> dict[str, Any]:
        cap = await self.registry.get(project_id, capability_id)
        if cap.status != "published":
            raise AppError("capability_not_published", "Capability is not published", status_code=403)
        if cap.operation != "read":
            raise AppError("capability_not_readonly", "Only read capabilities may execute", status_code=403)

        config = json.loads(cap.config_json or "{}")
        if cap.kind == "semantic_data":
            # Thin bridge: create ephemeral chat answer for question
            question = str(input_data.get("question") or "")
            if not question:
                raise AppError("invalid_input", "question is required", status_code=400)
            chat = ChatBIService(self.session)
            session = await chat.create_session(
                project_id=project_id,
                user_id=actor_user_id,
                title=f"cap:{cap.name}",
            )
            msg = await chat.ask(
                project_id=project_id,
                session_id=session.id,
                user_id=actor_user_id,
                question=question,
                datasource_id=config.get("datasource_id"),
                use_demo_rows=bool(config.get("use_demo_rows", True)),
            )
            return {
                "capability_id": cap.id,
                "kind": cap.kind,
                "content_markdown": msg.content_markdown,
                "sql": msg.sql_text,
            }

        if cap.kind == "functional":
            # Placeholder until OpenAPI adapter (Task 10)
            return {
                "capability_id": cap.id,
                "kind": cap.kind,
                "status": "not_wired",
                "message": "Functional execution lands in Task 10",
                "input": input_data,
                "config": config,
            }

        raise AppError("unsupported_kind", f"Unsupported capability kind: {cap.kind}", status_code=400)
