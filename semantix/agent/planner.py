from typing import Any

from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    capability_name: str | None = None
    capability_id: str | None = None
    kind: str = "semantic_data"
    input_template: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[int] = Field(default_factory=list)
    rationale: str = ""


class Planner:
    """Thin hybrid planner: keyword/heuristic routing (LLM optional later)."""

    async def plan(self, question: str, discovered: list[Any]) -> list[PlanStep]:
        q = question.strip()
        by_name = {getattr(c, "name", None): c for c in discovered}
        steps: list[PlanStep] = []

        wants_online = any(k in q for k in ("在线率", "online"))
        wants_alarms = any(k in q for k in ("告警", "alarm"))
        wants_lowest = any(k in q for k in ("最低", "lowest", "最差"))
        hybrid = wants_online and wants_alarms

        if hybrid or (wants_online and wants_lowest and wants_alarms):
            # Step 0: semantic low online-rate devices
            steps.append(
                PlanStep(
                    capability_name="semantic.query",
                    kind="semantic_data",
                    input_template={
                        "question": "找出最近 7 天在线率最低的 5 台设备",
                        "use_demo_rows": True,
                        "scenario": "lowest_online_devices",
                    },
                    rationale="先查语义侧在线率最低设备",
                )
            )
            alarm_cap = by_name.get("get_device_alarms")
            steps.append(
                PlanStep(
                    capability_name="get_device_alarms",
                    capability_id=getattr(alarm_cap, "id", None) if alarm_cap else None,
                    kind="functional",
                    input_template={"device_ids_from_step": 0, "limit": 5},
                    depends_on=[0],
                    rationale="再按设备 ID 拉取告警",
                )
            )
            return steps

        if wants_alarms and not wants_online:
            device_id = _extract_device_id(q) or "tacey_002"
            alarm_cap = by_name.get("get_device_alarms")
            steps.append(
                PlanStep(
                    capability_name="get_device_alarms",
                    capability_id=getattr(alarm_cap, "id", None) if alarm_cap else None,
                    kind="functional",
                    input_template={"device_id": device_id},
                    rationale="单设备告警查询",
                )
            )
            return steps

        if wants_online:
            steps.append(
                PlanStep(
                    capability_name="semantic.query",
                    kind="semantic_data",
                    input_template={"question": q, "use_demo_rows": True, "scenario": "online_rate"},
                    rationale="语义在线率查询",
                )
            )
            return steps

        # Default: single semantic ask
        steps.append(
            PlanStep(
                capability_name="semantic.query",
                kind="semantic_data",
                input_template={"question": q, "use_demo_rows": True},
                rationale="默认语义问答",
            )
        )
        return steps


def _extract_device_id(question: str) -> str | None:
    # Prefer explicit demo id patterns like tacey_002
    import re

    m = re.search(r"(tacey_\d+|device_[a-zA-Z0-9_]+|[A-Za-z]+_\d+)", question)
    return m.group(1) if m else None
