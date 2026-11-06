from semantix.engines.base import EngineSql


class FixtureEngineAdapter:
    """Deterministic SQL for MVP demo questions when Wren/Vanna are unavailable."""

    async def generate_sql(self, question: str, context: dict) -> EngineSql:
        q = question.strip()
        if "在线率" in q:
            return EngineSql(
                sql=(
                    "SELECT project_id, "
                    "SUM(CASE WHEN is_online THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*), 0) "
                    "AS online_rate "
                    "FROM devices "
                    "WHERE observed_at >= NOW() - INTERVAL '7 days' "
                    "GROUP BY project_id "
                    "ORDER BY online_rate ASC"
                ),
                engine="fixture",
                rationale="Matched device online rate demo question",
            )
        if "告警" in q:
            device_id = "tacey_002"
            for token in q.replace("，", " ").replace(",", " ").split():
                if token.startswith("tacey_") or token.startswith("device_"):
                    device_id = token
                    break
            return EngineSql(
                sql=(
                    "SELECT alarm_id, device_id, severity, message, raised_at "
                    "FROM device_alarms "
                    f"WHERE device_id = '{device_id}' "
                    "AND raised_at >= NOW() - INTERVAL '1 day' "
                    "ORDER BY raised_at DESC"
                ),
                engine="fixture",
                rationale="Matched device alarms demo question",
            )
        raise NotImplementedError(f"No fixture SQL for question: {question}")
