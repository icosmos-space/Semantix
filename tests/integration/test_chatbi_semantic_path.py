import pytest


@pytest.mark.asyncio
async def test_chatbi_online_rate_demo(client):
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "chat@b.com", "password": "secret123", "display_name": "Chat"},
    )
    assert r.status_code == 201
    r = await client.post("/api/v1/auth/login", json={"email": "chat@b.com", "password": "secret123"})
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = await client.post("/api/v1/projects", headers=headers, json={"name": "Chat", "slug": "chat-demo"})
    assert r.status_code == 201
    project_id = r.json()["id"]

    r = await client.post(
        f"/api/v1/projects/{project_id}/chatbi/sessions",
        headers=headers,
        json={"title": "demo"},
    )
    assert r.status_code == 201
    session_id = r.json()["id"]

    r = await client.post(
        f"/api/v1/projects/{project_id}/chatbi/sessions/{session_id}/messages",
        headers=headers,
        json={
            "content": "查询各项目最近 7 天的设备在线率。",
            "use_demo_rows": True,
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["role"] == "assistant"
    assert "```GPT-Vis" in body["content_markdown"]
    assert "```sql" in body["content_markdown"]
    assert body["sql"]
    assert body["rows"]
