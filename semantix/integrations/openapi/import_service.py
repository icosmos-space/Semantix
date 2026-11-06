import json
from typing import Any
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from semantix.capability.registry import CapabilityRegistry
from semantix.core.errors import AppError
from semantix.integrations.openapi.overlay import merge_overlay
from semantix.models.integration import Integration, RawOpenApiSpec, ToolSemanticOverlay
from semantix.security.crypto import encrypt_secret


def _extract_operations(spec: dict[str, Any]) -> list[dict[str, Any]]:
    paths = spec.get("paths") or {}
    ops: list[dict[str, Any]] = []
    for path, item in paths.items():
        if not isinstance(item, dict):
            continue
        for method, detail in item.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete", "head", "options"}:
                continue
            if not isinstance(detail, dict):
                continue
            ops.append(
                {
                    "operation_id": detail.get("operationId") or f"{method}_{path}",
                    "method": method.lower(),
                    "path": path,
                    "summary": detail.get("summary"),
                    "description": detail.get("description"),
                }
            )
    return ops


class OpenApiImportService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_integration(
        self,
        *,
        project_id: str,
        name: str,
        base_url: str,
        auth_type: str = "none",
        auth_token: str | None = None,
    ) -> Integration:
        host = urlparse(base_url).hostname or ""
        integration = Integration(
            project_id=project_id,
            name=name,
            base_url=base_url.rstrip("/"),
            auth_type=auth_type,
            auth_token_encrypted=encrypt_secret(auth_token) if auth_token else None,
            allowed_hosts=host,
        )
        self.session.add(integration)
        await self.session.commit()
        await self.session.refresh(integration)
        return integration

    async def import_spec(
        self,
        *,
        project_id: str,
        integration_id: str,
        spec: dict[str, Any],
    ) -> dict[str, Any]:
        integration = await self.session.scalar(
            select(Integration).where(
                Integration.id == integration_id,
                Integration.project_id == project_id,
            )
        )
        if integration is None:
            raise AppError("not_found", "Integration not found", status_code=404)

        raw = RawOpenApiSpec(
            integration_id=integration.id,
            version_label="import",
            spec_json=json.dumps(spec),
        )
        self.session.add(raw)

        created_overlays = 0
        created_caps = 0
        registry = CapabilityRegistry(self.session)
        for op in _extract_operations(spec):
            existing = await self.session.scalar(
                select(ToolSemanticOverlay).where(
                    ToolSemanticOverlay.integration_id == integration.id,
                    ToolSemanticOverlay.operation_id == op["operation_id"],
                )
            )
            if existing:
                # Sync must NOT overwrite overlay semantics; only keep method/path fresh on raw.
                continue

            name = op["operation_id"]
            # Prefer friendly name for demo alarms endpoint
            if op["path"] == "/api/device/{device_id}/alarms" and op["method"] == "get":
                name = "get_device_alarms"
                description = "查询指定设备的历史告警和未处理告警"
                intents = ["查询设备告警", "查看设备异常", "获取未处理告警"]
            else:
                description = op.get("summary") or op.get("description") or name
                intents = []

            overlay = ToolSemanticOverlay(
                integration_id=integration.id,
                operation_id=op["operation_id"],
                name=name,
                description=description,
                intents_json=json.dumps(intents, ensure_ascii=False),
                entities_json=json.dumps([]),
                read_only_confirmed=False,
                method=op["method"].upper(),
                path=op["path"],
            )
            self.session.add(overlay)
            await self.session.flush()
            created_overlays += 1

            cap = await registry.register(
                project_id=project_id,
                name=name,
                kind="functional",
                description=description,
                source="openapi",
                source_ref=f"{integration.id}:{op['operation_id']}",
                config={
                    "integration_id": integration.id,
                    "operation_id": op["operation_id"],
                    "method": op["method"].upper(),
                    "path": op["path"],
                    "base_url": integration.base_url,
                },
                status="draft",
            )
            overlay.capability_id = cap.id
            created_caps += 1

        await self.session.commit()
        return {
            "raw_spec_id": raw.id,
            "overlays_created": created_overlays,
            "capabilities_created": created_caps,
        }

    async def update_overlay(
        self,
        *,
        project_id: str,
        overlay_id: str,
        name: str | None = None,
        description: str | None = None,
        intents: list[str] | None = None,
        entities: list[str] | None = None,
        read_only_confirmed: bool | None = None,
    ) -> ToolSemanticOverlay:
        overlay = await self.session.scalar(
            select(ToolSemanticOverlay)
            .join(Integration, Integration.id == ToolSemanticOverlay.integration_id)
            .where(
                ToolSemanticOverlay.id == overlay_id,
                Integration.project_id == project_id,
            )
        )
        if overlay is None:
            raise AppError("not_found", "Overlay not found", status_code=404)
        if name is not None:
            overlay.name = name
        if description is not None:
            overlay.description = description
        if intents is not None:
            overlay.intents_json = json.dumps(intents, ensure_ascii=False)
        if entities is not None:
            overlay.entities_json = json.dumps(entities, ensure_ascii=False)
        if read_only_confirmed is not None:
            overlay.read_only_confirmed = read_only_confirmed
        await self.session.commit()
        await self.session.refresh(overlay)
        return overlay

    async def publish_overlay_capability(
        self,
        *,
        project_id: str,
        overlay_id: str,
    ) -> dict[str, Any]:
        overlay = await self.session.scalar(
            select(ToolSemanticOverlay)
            .join(Integration, Integration.id == ToolSemanticOverlay.integration_id)
            .where(
                ToolSemanticOverlay.id == overlay_id,
                Integration.project_id == project_id,
            )
        )
        if overlay is None:
            raise AppError("not_found", "Overlay not found", status_code=404)
        if not overlay.read_only_confirmed:
            raise AppError(
                "readonly_not_confirmed",
                "Confirm read-only semantics before publishing",
                status_code=400,
            )
        if not overlay.capability_id:
            raise AppError("missing_capability", "Overlay has no linked capability", status_code=400)
        cap = await CapabilityRegistry(self.session).publish(project_id, overlay.capability_id)
        return {"overlay_id": overlay.id, "capability_id": cap.id, "status": cap.status}

    def preview_effective(self, raw_operation: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
        return merge_overlay(raw_operation, overlay)
