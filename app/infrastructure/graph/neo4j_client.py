from neo4j import GraphDatabase


class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str, database: str) -> None:
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def query(self, cypher: str, params: dict | None = None) -> list[dict]:
        with self.driver.session(database=self.database) as session:
            result = session.run(cypher, params or {})
            return [record.data() for record in result]

    def close(self) -> None:
        self.driver.close()
