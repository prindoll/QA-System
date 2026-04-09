from app.infrastructure.graph.cypher_repository import CypherRepository


class GraphIndexer:
    def __init__(self, repo: CypherRepository) -> None:
        self.repo = repo

    def index(self, normalized_payload: dict, chunk_id: str, source_doc_id: str, chunk_text: str) -> None:
        entities = normalized_payload.get("entities", [])
        relationships = normalized_payload.get("relationships", [])
        prepared_relationships = self._prepare_relationships(
            relationships=relationships,
            chunk_id=chunk_id,
            source_doc_id=source_doc_id,
        )

        self.repo.upsert_entities(entities)
        self.repo.upsert_mentions(
            entities=entities,
            chunk_id=chunk_id,
            source_doc_id=source_doc_id,
            chunk_text=chunk_text,
        )
        self.repo.upsert_relationships(prepared_relationships)

    def _prepare_relationships(
        self,
        relationships: list[dict],
        chunk_id: str,
        source_doc_id: str,
    ) -> list[dict]:
        prepared: list[dict] = []
        for rel in relationships:
            cloned = dict(rel)
            cloned["source_doc_id"] = str(cloned.get("source_doc_id") or source_doc_id)
            cloned["source_chunk_id"] = str(cloned.get("source_chunk_id") or chunk_id)
            prepared.append(cloned)
        return prepared
