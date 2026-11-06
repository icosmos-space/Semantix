import pytest

from semantix.engines.sqlglot_policy import SqlPolicyError, assert_readonly_sql


def test_allows_select():
    assert assert_readonly_sql("SELECT 1") == "SELECT 1"


def test_allows_with():
    sql = "WITH x AS (SELECT 1 AS a) SELECT * FROM x"
    assert "SELECT" in assert_readonly_sql(sql).upper()


def test_rejects_insert():
    with pytest.raises(SqlPolicyError):
        assert_readonly_sql("INSERT INTO t VALUES (1)")


def test_rejects_multi_statement():
    with pytest.raises(SqlPolicyError):
        assert_readonly_sql("SELECT 1; DROP TABLE t")


def test_rejects_pg_catalog():
    with pytest.raises(SqlPolicyError):
        assert_readonly_sql("SELECT * FROM pg_catalog.pg_tables")
