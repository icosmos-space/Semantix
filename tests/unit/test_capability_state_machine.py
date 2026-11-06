import pytest

from semantix.core.errors import AppError
from semantix.capability.executor import CapabilityExecutor


@pytest.mark.asyncio
async def test_cannot_execute_draft(monkeypatch):
    class FakeCap:
        status = "draft"
        operation = "read"
        kind = "semantic_data"
        id = "c1"
        config_json = "{}"

    class FakeRegistry:
        async def get(self, project_id, capability_id):
            return FakeCap()

    executor = CapabilityExecutor(session=None)  # type: ignore[arg-type]
    monkeypatch.setattr(executor, "registry", FakeRegistry())
    with pytest.raises(AppError) as ei:
        await executor.execute(
            project_id="p",
            capability_id="c1",
            input_data={"question": "x"},
            actor_user_id="u",
        )
    assert ei.value.code == "capability_not_published"
