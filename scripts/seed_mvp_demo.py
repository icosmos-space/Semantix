"""Seed MVP demo capabilities (safe to re-run against empty project via API notes).

This script prints a ready-to-import OpenAPI snippet and registers guidance.
For automated DB seed, prefer the integration test fixtures / Studio UI.
"""

from __future__ import annotations

SAMPLE_OPENAPI = {
    "openapi": "3.0.0",
    "info": {"title": "Device Alarms API", "version": "1.0.0"},
    "paths": {
        "/api/device/{device_id}/alarms": {
            "get": {
                "operationId": "getAlarms",
                "summary": "List device alarms",
                "parameters": [
                    {
                        "name": "device_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {"200": {"description": "ok"}},
            }
        }
    },
}


def main() -> None:
    import json

    print("=== MVP OpenAPI sample (paste into Studio → 系统集成 → 导入) ===")
    print(json.dumps(SAMPLE_OPENAPI, ensure_ascii=False, indent=2))
    print()
    print("Suggested integration base_url: http://127.0.0.1:18080")
    print("After import: confirm read-only on get_device_alarms → publish")
    print("ChatBI prompts: see docs/demo/mvp-scenarios.md")


if __name__ == "__main__":
    main()
