from typing import Any
from urllib.parse import urlparse

import httpx

from semantix.core.config import get_settings
from semantix.core.errors import AppError


def assert_host_allowed(url: str, *, extra_allowed: list[str] | None = None) -> None:
    settings = get_settings()
    allowed = {
        h.strip().lower()
        for h in settings.http_allowlist_hosts.split(",")
        if h.strip()
    }
    if extra_allowed:
        allowed.update(h.strip().lower() for h in extra_allowed if h.strip())
    host = (urlparse(url).hostname or "").lower()
    if not host or host not in allowed:
        raise AppError(
            "host_not_allowed",
            f"Host '{host}' is not in the Functional HTTP allowlist",
            status_code=400,
        )


async def invoke_http(
    *,
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
    extra_allowed_hosts: list[str] | None = None,
) -> dict[str, Any]:
    settings = get_settings()
    assert_host_allowed(url, extra_allowed=extra_allowed_hosts)
    timeout = httpx.Timeout(settings.http_timeout_s)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
        response = await client.request(
            method.upper(),
            url,
            headers=headers,
            params=params,
            json=json_body,
        )
    content = response.content
    if len(content) > settings.http_max_response_bytes:
        raise AppError("response_too_large", "Functional API response exceeds size limit", status_code=400)
    try:
        data = response.json()
    except Exception:
        data = {"raw": content.decode("utf-8", errors="replace")}
    if response.status_code >= 400:
        raise AppError(
            "functional_http_error",
            f"Upstream returned HTTP {response.status_code}",
            status_code=400,
            details={"status_code": response.status_code, "body": data},
        )
    return {"status_code": response.status_code, "data": data}
