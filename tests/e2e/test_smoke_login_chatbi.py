"""HTTP smoke: register → login → project → ChatBI online-rate demo."""

import pytest


@pytest.mark.asyncio
async def test_smoke_login_chatbi(client):
    email = "smoke@example.com"
    password = "secret123"

    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "display_name": "Smoke"},
    )
    assert r.status_code == 201, r.text

    r = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

    r = await client.post(
        "/api/v1/projects",
        headers=headers,
        json={"name": "Smoke", "slug": "smoke"},
    )
    assert r.status_code == 201, r.text
    project_id = r.json()["id"]

    r = await client.post(
        f"/api/v1/projects/{project_id}/chatbi/sessions",
        headers=headers,
        json={"title": "smoke"},
    )
    assert r.status_code == 201
    session_id = r.json()["id"]

    r = await client.post(
        f"/api/v1/projects/{project_id}/chatbi/sessions/{session_id}/messages",
        headers=headers,
        json={"content": "查询各项目最近 7 天的设备在线率。", "use_demo_rows": True},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["role"] == "assistant"
    assert "```GPT-Vis" in body["content_markdown"]
    assert body["rows"]
