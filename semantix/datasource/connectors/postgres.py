from typing import Any

import asyncpg


class PostgresConnector:
    def __init__(
        self,
        *,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
    ):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password

    async def _connect(self) -> asyncpg.Connection:
        return await asyncpg.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            database=self.database,
            timeout=10,
        )

    async def test_connection(self) -> None:
        conn = await self._connect()
        try:
            await conn.fetchval("SELECT 1")
        finally:
            await conn.close()

    async def discover_schema(self) -> dict[str, Any]:
        conn = await self._connect()
        try:
            rows = await conn.fetch(
                """
                SELECT
                  table_schema,
                  table_name,
                  column_name,
                  data_type,
                  is_nullable
                FROM information_schema.columns
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                ORDER BY table_schema, table_name, ordinal_position
                """
            )
            fks = await conn.fetch(
                """
                SELECT
                  tc.table_schema,
                  tc.table_name,
                  kcu.column_name,
                  ccu.table_schema AS foreign_table_schema,
                  ccu.table_name AS foreign_table_name,
                  ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                 AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                """
            )
        finally:
            await conn.close()

        tables: dict[tuple[str, str], dict[str, Any]] = {}
        for r in rows:
            key = (r["table_schema"], r["table_name"])
            table = tables.setdefault(
                key,
                {
                    "schema": r["table_schema"],
                    "name": r["table_name"],
                    "columns": [],
                    "foreign_keys": [],
                },
            )
            table["columns"].append(
                {
                    "name": r["column_name"],
                    "type": r["data_type"],
                    "nullable": r["is_nullable"] == "YES",
                }
            )
        for fk in fks:
            key = (fk["table_schema"], fk["table_name"])
            if key in tables:
                tables[key]["foreign_keys"].append(
                    {
                        "column": fk["column_name"],
                        "ref_schema": fk["foreign_table_schema"],
                        "ref_table": fk["foreign_table_name"],
                        "ref_column": fk["foreign_column_name"],
                    }
                )
        return {
            "database": self.database,
            "tables": list(tables.values()),
        }
