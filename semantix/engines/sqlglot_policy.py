import sqlglot
from sqlglot import exp


class SqlPolicyError(ValueError):
    pass


_BLOCKED_TYPES = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Merge,
    exp.Create,
    exp.Drop,
    exp.Alter,
    exp.Grant,
    exp.Command,
)


def assert_readonly_sql(sql: str, dialect: str = "postgres") -> str:
    text = (sql or "").strip().rstrip(";")
    if not text:
        raise SqlPolicyError("SQL is empty")

    try:
        statements = sqlglot.parse(text, read=dialect)
    except sqlglot.errors.ParseError as exc:
        raise SqlPolicyError(f"SQL parse error: {exc}") from exc

    if len(statements) != 1 or statements[0] is None:
        raise SqlPolicyError("Only a single SQL statement is allowed")

    statement = statements[0]
    if not isinstance(statement, (exp.Select, exp.Union)):
        # WITH ... SELECT is still Select
        if not isinstance(statement, exp.Query):
            raise SqlPolicyError("Only SELECT / WITH queries are allowed")

    for node in statement.walk():
        if isinstance(node, _BLOCKED_TYPES):
            raise SqlPolicyError(f"Disallowed SQL operation: {type(node).__name__}")
        if isinstance(node, exp.Table):
            catalog = (node.catalog or "").lower()
            db = (node.db or "").lower()
            if catalog in {"pg_catalog", "information_schema"} or db in {
                "pg_catalog",
                "information_schema",
            }:
                raise SqlPolicyError("Access to system catalogs is not allowed")

    return statement.sql(dialect=dialect)
