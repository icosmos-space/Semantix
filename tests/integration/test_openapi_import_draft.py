import pytest


SAMPLE_OPENAPI = {
    "openapi": "3.0.0",
    "info": {"title": "Device API", "version": "1.0.0"},
    "paths": {
        "/api/device/{device_id}/alarms": {
            "get": {
                "operationId": "getAlarms",
                "summary": "upstream summary",
                "responses": {"200": {"description": "ok"}},
            }
        }
    },
}


@pytest.mark.asyncio
async def test_openapi_import_creates_draft_capability(client):
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "openapi@b.com", "password": "secret123", "display_name": "O"},
    )
    assert r.status_code == 201, r.text
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "openapi@b.com", "password": "secret123"},
    )
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = await client.post(
        "/api/v1/projects",
        headers=headers,
        json={"name": "OpenAPI Demo", "slug": "openapi-demo"},
    )
    assert r.status_code == 201, r.text
    project_id = r.json()["id"]

    r = await client.post(
        f"/api/v1/projects/{project_id}/integrations",
        headers=headers,
        json={
            "name": "device-api",
            "base_url": "http://127.0.0.1:18080",
            "auth_type": "none",
        },
    )
    assert r.status_code == 201, r.text
    integration_id = r.json()["id"]

    r = await client.post(
        f"/api/v1/projects/{project_id}/integrations/{integration_id}/import",
        headers=headers,
        json={"openapi": SAMPLE_OPENAPI},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["overlays_created"] == 1
    assert body["capabilities_created"] == 1

    r = await client.get(
        f"/api/v1/projects/{project_id}/integrations/{integration_id}/overlays",
        headers=headers,
    )
    assert r.status_code == 200
    overlays = r.json()
    assert len(overlays) == 1
    overlay = overlays[0]
    assert overlay["name"] == "get_device_alarms"
    assert overlay["read_only_confirmed"] is False
    assert overlay["capability_id"]

    r = await client.get(
        f"/api/v1/projects/{project_id}/capabilities",
        headers=headers,
    )
    caps = r.json()
    functional = [c for c in caps if c["name"] == "get_device_alarms"]
    assert len(functional) == 1
    assert functional[0]["status"] == "draft"
    assert functional[0]["kind"] == "functional"

    # Publish without read-only confirmation must fail
    r = await client.post(
        f"/api/v1/projects/{project_id}/integrations/overlays/{overlay['id']}/publish",
        headers=headers,
    )
    assert r.status_code == 400
    assert r.json()["code"] == "readonly_not_confirmed"

    r = await client.patch(
        f"/api/v1/projects/{project_id}/integrations/overlays/{overlay['id']}",
        headers=headers,
        json={"read_only_confirmed": True, "description": "查询设备告警"},
    )
    assert r.status_code == 200
    assert r.json()["read_only_confirmed"] is True

    r = await client.post(
        f"/api/v1/projects/{project_id}/integrations/overlays/{overlay['id']}/publish",
        headers=headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "published"

    # Re-import must not clobber overlay description / create duplicate
    r = await client.post(
        f"/api/v1/projects/{project_id}/integrations/{integration_id}/import",
        headers=headers,
        json={"openapi": SAMPLE_OPENAPI},
    )
    assert r.status_code == 200
    assert r.json()["overlays_created"] == 0

    r = await client.get(
        f"/api/v1/projects/{project_id}/integrations/{integration_id}/overlays",
        headers=headers,
    )
    assert r.json()[0]["description"] == "查询设备告警"
