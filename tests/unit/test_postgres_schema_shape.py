from semantix.datasource.connectors.postgres import PostgresConnector


def test_connector_init_fields():
    c = PostgresConnector(
        host="localhost",
        port=5432,
        database="db",
        username="u",
        password="p",
    )
    assert c.host == "localhost"
    assert c.port == 5432
