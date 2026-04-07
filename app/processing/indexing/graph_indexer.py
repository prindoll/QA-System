from app.infrastructure.graph.cypher_repository import CypherRepository


class GraphIndexer:
    def __init__(self, repo: CypherRepository) -> None:
        self.repo = repo

    def index(self, normalized_payload: dict) -> None:
        self.repo.upsert_entities(normalized_payload.get("entities", []))
        self.repo.upsert_relationships(normalized_payload.get("relationships", []))
