import pytest

from semantix.agent.planner import Planner


class Cap:
    def __init__(self, name: str, id: str = "cap-1"):
        self.name = name
        self.id = id


@pytest.mark.asyncio
async def test_planner_hybrid_orders_semantic_then_alarms():
    planner = Planner()
    steps = await planner.plan(
        "找出最近 7 天在线率最低的 5 台设备，并查询它们最近的告警情况。",
        [Cap("get_device_alarms", "alarm-cap")],
    )
    assert len(steps) == 2
    assert steps[0].kind == "semantic_data"
    assert steps[1].kind == "functional"
    assert steps[1].capability_id == "alarm-cap"
    assert steps[1].depends_on == [0]


@pytest.mark.asyncio
async def test_planner_single_device_alarm():
    planner = Planner()
    steps = await planner.plan(
        "查询设备 tacey_002 最近一天的告警。",
        [Cap("get_device_alarms")],
    )
    assert len(steps) == 1
    assert steps[0].kind == "functional"
    assert steps[0].input_template["device_id"] == "tacey_002"


@pytest.mark.asyncio
async def test_planner_online_rate_only():
    planner = Planner()
    steps = await planner.plan("查询各项目最近 7 天的设备在线率。", [])
    assert len(steps) == 1
    assert steps[0].kind == "semantic_data"
