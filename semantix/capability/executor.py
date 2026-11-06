import json
from typing import Any
from urllib.parse import urljoin

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from semantix.capability.registry import CapabilityRegistry
from semantix.core.errors import AppError
from semantix.integrations.openapi.http_adapter import invoke_http
from semantix.models.integration import Integration
from semantix.query.chatbi import ChatBIService
from semantix.security.crypto import decrypt_secret


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
            return await self._execute_functional(project_id, cap.id, config, input_data)

        raise AppError("unsupported_kind", f"Unsupported capability kind: {cap.kind}", status_code=400)

    async def _execute_functional(
        self,
        project_id: str,
        capability_id: str,
        config: dict[str, Any],
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        integration_id = config.get("integration_id")
        method = str(config.get("method") or "GET").upper()
        path = str(config.get("path") or "/")
        base_url = str(config.get("base_url") or "")

        # Demo/mock path without live upstream
        if config.get("mock_response") is not None:
            return {
                "capability_id": capability_id,
                "kind": "functional",
                "status": "ok",
                "data": config["mock_response"],
                "input": input_data,
            }

        if not integration_id or not base_url:
            raise AppError("invalid_config", "Functional capability missing HTTP config", status_code=400)

        integration = await self.session.scalar(
            select(Integration).where(
                Integration.id == integration_id,
                Integration.project_id == project_id,
            )
        )
        if integration is None:
            raise AppError("not_found", "Integration not found", status_code=404)

        # Path template substitution
        resolved_path = path
        for key, value in input_data.items():
            resolved_path = resolved_path.replace("{" + str(key) + "}", str(value))
        url = urljoin(integration.base_url.rstrip("/") + "/", resolved_path.lstrip("/"))

        headers: dict[str, str] = {}
        if integration.auth_type == "bearer" and integration.auth_token_encrypted:
            headers["Authorization"] = f"Bearer {decrypt_secret(integration.auth_token_encrypted)}"

        query_params = {
            k: v
            for k, v in input_data.items()
            if "{" + k + "}" not in path
        }
        extra_hosts = [h.strip() for h in (integration.allowed_hosts or "").split(",") if h.strip()]
        result = await invoke_http(
            method=method,
            url=url,
            headers=headers,
            params=query_params if method == "GET" else None,
            json_body=None if method == "GET" else input_data,
            extra_allowed_hosts=extra_hosts,
        )
        return {
            "capability_id": capability_id,
            "kind": "functional",
            "status": "ok",
            "upstream": result,
            "url": url,
            "method": method,
        }
