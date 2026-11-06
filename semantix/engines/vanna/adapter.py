from semantix.engines.base import EngineSql
from semantix.engines.fixture import FixtureEngineAdapter


class VannaAdapter:
    """Placeholder Vanna adapter — falls back to fixture until Vanna is wired."""

    def __init__(self) -> None:
        self._fallback = FixtureEngineAdapter()

    async def generate_sql(self, question: str, context: dict) -> EngineSql:
        result = await self._fallback.generate_sql(question, context)
        return EngineSql(sql=result.sql, engine="vanna", rationale=result.rationale)
