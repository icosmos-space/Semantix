from semantix.engines.base import EngineSql
from semantix.engines.fixture import FixtureEngineAdapter


class WrenAdapter:
    """Placeholder Wren Core adapter — falls back to fixture until Wren is wired."""

    def __init__(self) -> None:
        self._fallback = FixtureEngineAdapter()

    async def generate_sql(self, question: str, context: dict) -> EngineSql:
        result = await self._fallback.generate_sql(question, context)
        return EngineSql(sql=result.sql, engine="wren", rationale=result.rationale)
