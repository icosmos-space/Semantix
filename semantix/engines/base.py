from typing import Protocol

from pydantic import BaseModel


class EngineSql(BaseModel):
    sql: str
    engine: str  # "wren" | "vanna" | "fixture"
    rationale: str | None = None


class EngineAdapter(Protocol):
    async def generate_sql(self, question: str, context: dict) -> EngineSql: ...
