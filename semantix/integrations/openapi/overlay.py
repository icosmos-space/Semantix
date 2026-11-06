from typing import Any


def merge_overlay(raw_operation: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Merge upstream OpenAPI operation with user-maintained semantic overlay.

    Overlay fields win for name/description/intents/entities.
    Raw fields provide method/path/operation_id fallbacks.
    """
    return {
        "operation_id": raw_operation.get("operation_id") or overlay.get("operation_id"),
        "method": (raw_operation.get("method") or overlay.get("method") or "get").lower(),
        "path": raw_operation.get("path") or overlay.get("path") or "/",
        "summary": raw_operation.get("summary"),
        "name": overlay.get("name") or raw_operation.get("operation_id") or "unnamed_tool",
        "description": overlay.get("description")
        or raw_operation.get("summary")
        or raw_operation.get("description")
        or "",
        "intents": list(overlay.get("intents") or []),
        "entities": list(overlay.get("entities") or []),
        "read_only_confirmed": bool(overlay.get("read_only_confirmed", False)),
    }
