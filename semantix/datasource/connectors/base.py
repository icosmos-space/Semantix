from typing import Any, Protocol


class DataSourceConnector(Protocol):
    async def test_connection(self) -> None: ...

    async def discover_schema(self) -> dict[str, Any]: ...
