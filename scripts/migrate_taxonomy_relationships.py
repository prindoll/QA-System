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


def migrate_relates_to_predicate_to_typed() -> dict[str, int]:
    neo4j = _build_client()
    migrated: dict[str, int] = {}

    for rel_type in ("IS_A", "PART_OF"):
        cypher = f"""
        MATCH (s:Entity)-[r:RELATES_TO]->(t:Entity)
        WHERE r.predicate = '{rel_type}'
        WITH s, t, r, coalesce(r.relation_id, 'rel_mig_' + toString(id(s)) + '_{rel_type}_' + toString(id(t))) AS relation_id
        MERGE (s)-[nr:{rel_type} {{relation_id: relation_id}}]->(t)
        ON CREATE SET
          nr.predicate = '{rel_type}',
          nr.confidence = coalesce(r.confidence, 0.0),
          nr.evidence_text = coalesce(r.evidence_text, ''),
          nr.source_doc_id = coalesce(r.source_doc_id, ''),
          nr.source_chunk_id = coalesce(r.source_chunk_id, ''),
          nr.created_at = coalesce(r.created_at, datetime())
        ON MATCH SET
          nr.confidence = CASE WHEN coalesce(r.confidence, 0.0) > coalesce(nr.confidence, 0.0) THEN r.confidence ELSE nr.confidence END,
          nr.evidence_text = coalesce(nr.evidence_text, r.evidence_text),
          nr.source_doc_id = coalesce(nr.source_doc_id, r.source_doc_id),
          nr.source_chunk_id = coalesce(nr.source_chunk_id, r.source_chunk_id),
          nr.updated_at = datetime()
        WITH r
        DELETE r
        RETURN count(*) AS migrated
        """
        rows = neo4j.query(cypher)
        migrated[rel_type] = int(rows[0]["migrated"]) if rows else 0

    neo4j.close()
    return migrated


def main() -> None:
    stats = migrate_relates_to_predicate_to_typed()
    print(
        "Migrated taxonomy relationships: "
        f"IS_A={stats.get('IS_A', 0)}, PART_OF={stats.get('PART_OF', 0)}"
    )


if __name__ == "__main__":
    main()
