from app.core.config.settings import get_settings
from app.infrastructure.graph.neo4j_client import Neo4jClient
from app.processing.indexing.vector_indexer import VectorIndexer


def _build_neo4j_client() -> Neo4jClient:
    settings = get_settings()
    return Neo4jClient(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
        database=settings.neo4j_database,
    )


def _fetch_chunks(neo4j: Neo4jClient, missing_only: bool) -> list[dict]:
    where_clause = "WHERE c.embedding IS NULL AND coalesce(c.text, '') <> ''" if missing_only else ""
    return neo4j.query(
        f"""
        MATCH (c:Chunk)
        {where_clause}
        RETURN c.chunk_id AS chunk_id,
               c.source_doc_id AS source_doc_id,
               c.text AS text
        """
    )


def count_chunks_missing_embeddings() -> int:
    neo4j = _build_neo4j_client()
    rows = neo4j.query(
        """
        MATCH (c:Chunk)
        WHERE c.embedding IS NULL AND coalesce(c.text, '') <> ''
        RETURN count(c) AS n
        """
    )
    neo4j.close()
    return int(rows[0]["n"]) if rows else 0


def reindex_all_chunks() -> None:
    settings = get_settings()
    neo4j = _build_neo4j_client()
    rows = _fetch_chunks(neo4j=neo4j, missing_only=False)
    indexer = VectorIndexer(neo4j_client=neo4j, embedding_model=settings.openai_embedding_model)
    indexer.index_chunks(rows)
    neo4j.close()


def reindex_missing_chunks() -> int:
    settings = get_settings()
    neo4j = _build_neo4j_client()
    rows = _fetch_chunks(neo4j=neo4j, missing_only=True)
    if not rows:
        neo4j.close()
        return 0

    indexer = VectorIndexer(neo4j_client=neo4j, embedding_model=settings.openai_embedding_model)
    indexer.index_chunks(rows)
    neo4j.close()
    return len(rows)
