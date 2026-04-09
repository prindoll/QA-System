from app.core.config.settings import get_settings
from app.infrastructure.graph.neo4j_client import Neo4jClient


def _build_client() -> Neo4jClient:
    settings = get_settings()
    return Neo4jClient(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
        database=settings.neo4j_database,
    )


def backfill_mentions() -> int:
    neo4j = _build_client()
    cypher = """
    MATCH (s:Entity)-[r]->(t:Entity)
    WHERE type(r) IN ['RELATES_TO', 'IS_A', 'PART_OF']
      AND coalesce(r.source_chunk_id, '') <> ''
    MATCH (c:Chunk {chunk_id: r.source_chunk_id})
    MERGE (s)-[ms:MENTIONED_IN]->(c)
    ON CREATE SET
      ms.source_doc_id = coalesce(r.source_doc_id, c.source_doc_id, ''),
      ms.created_at = datetime()
    ON MATCH SET
      ms.source_doc_id = coalesce(ms.source_doc_id, r.source_doc_id, c.source_doc_id),
      ms.updated_at = datetime()
    MERGE (t)-[mt:MENTIONED_IN]->(c)
    ON CREATE SET
      mt.source_doc_id = coalesce(r.source_doc_id, c.source_doc_id, ''),
      mt.created_at = datetime()
    ON MATCH SET
      mt.source_doc_id = coalesce(mt.source_doc_id, r.source_doc_id, c.source_doc_id),
      mt.updated_at = datetime()
    RETURN count(*) AS rows
    """
    rows = neo4j.query(cypher)
    neo4j.close()
    return int(rows[0]["rows"]) if rows else 0


def main() -> None:
    count = backfill_mentions()
    print(f"Backfilled MENTIONED_IN from relationship evidence rows={count}")


if __name__ == "__main__":
    main()
