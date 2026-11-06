import pytest


@pytest.mark.asyncio
async def test_hybrid_alarms_flow(client):
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "hybrid@b.com", "password": "secret123", "display_name": "H"},
    )
    assert r.status_code == 201
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "hybrid@b.com", "password": "secret123"},
    )
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = await client.post(
        "/api/v1/projects",
        headers=headers,
        json={"name": "Hybrid", "slug": "hybrid-demo"},
    )
    project_id = r.json()["id"]

    # Publish functional capability used by planner
    r = await client.post(
        f"/api/v1/projects/{project_id}/capabilities",
        headers=headers,
        json={
            "name": "get_device_alarms",
            "kind": "functional",
            "description": "查询设备告警",
            "config": {
                "mock_response": {
                    "alarms": [
                        {"alarm_id": "M-1", "level": "critical", "message": "mock", "status": "open"}
                    ]
                }
            },
        },
    )
    assert r.status_code == 201, r.text
    cap_id = r.json()["id"]
    r = await client.post(
        f"/api/v1/projects/{project_id}/capabilities/{cap_id}/publish",
        headers=headers,
    )
    assert r.status_code == 200

    r = await client.post(
        f"/api/v1/projects/{project_id}/chatbi/sessions",
        headers=headers,
        json={"title": "hybrid"},
    )
    session_id = r.json()["id"]

    r = await client.post(
        f"/api/v1/projects/{project_id}/chatbi/sessions/{session_id}/messages",
        headers=headers,
        json={
            "content": "找出最近 7 天在线率最低的 5 台设备，并查询它们最近的告警情况。",
            "use_demo_rows": True,
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["role"] == "assistant"
    assert "混合查询计划" in body["content_markdown"]
    assert "tacey_002" in body["content_markdown"]
    assert "告警" in body["content_markdown"]
    assert body["execution_summary"]["status"] == "hybrid"
    assert len(body["execution_summary"]["steps"]) == 2

    # Scenario 2: single device alarms
    r = await client.post(
        f"/api/v1/projects/{project_id}/chatbi/sessions/{session_id}/messages",
        headers=headers,
        json={"content": "查询设备 tacey_002 最近一天的告警。", "use_demo_rows": True},
    )
    assert r.status_code == 201, r.text
    assert "tacey_002" in r.json()["content_markdown"]
    assert "A-1001" in r.json()["content_markdown"] or "告警" in r.json()["content_markdown"]
