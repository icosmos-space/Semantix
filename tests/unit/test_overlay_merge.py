from semantix.integrations.openapi.overlay import merge_overlay
from semantix.integrations.openapi.http_adapter import assert_host_allowed
from semantix.core.errors import AppError
import pytest


def test_sync_does_not_clobber_overlay_description():
    raw = {
        "operation_id": "getAlarms",
        "method": "get",
        "path": "/api/device/{device_id}/alarms",
    }
    overlay = {
        "name": "get_device_alarms",
        "description": "查询设备告警",
        "intents": ["查询设备告警"],
    }
    effective = merge_overlay(raw, overlay)
    assert effective["name"] == "get_device_alarms"
    raw2 = {**raw, "summary": "new upstream summary"}
    effective2 = merge_overlay(raw2, overlay)
    assert effective2["description"] == "查询设备告警"
    assert effective2["intents"] == ["查询设备告警"]


def test_host_allowlist_rejects_unknown(monkeypatch):
    from semantix.core.config import Settings

    monkeypatch.setattr(
        "semantix.integrations.openapi.http_adapter.get_settings",
        lambda: Settings(http_allowlist_hosts="localhost,127.0.0.1"),
    )
    with pytest.raises(AppError) as ei:
        assert_host_allowed("http://evil.example/api")
    assert ei.value.code == "host_not_allowed"
    assert_host_allowed("http://localhost:8080/api")
