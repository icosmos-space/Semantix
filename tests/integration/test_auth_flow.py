import pytest


@pytest.mark.asyncio
async def test_register_login_create_project(client):
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "a@b.com", "password": "secret123", "display_name": "A"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["email"] == "a@b.com"

    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "a@b.com", "password": "secret123"},
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]

    r = await client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Demo", "slug": "demo"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["slug"] == "demo"

    r = await client.get("/api/v1/projects", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.json()) == 1
