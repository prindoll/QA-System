from app.core.config.settings import get_settings
from app.infrastructure.graph.neo4j_client import Neo4jClient
from app.processing.indexing.vector_indexer import VectorIndexer


def reindex_all_chunks() -> None:
    settings = get_settings()
    neo4j = Neo4jClient(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
        database=settings.neo4j_database,
    )

    rows = neo4j.query(
        """
        MATCH (c:Chunk)
        RETURN c.chunk_id AS chunk_id,
               c.source_doc_id AS source_doc_id,
               c.text AS text
        """
    )

    indexer = VectorIndexer(neo4j_client=neo4j, embedding_model=settings.openai_embedding_model)
    indexer.index_chunks(rows)
    neo4j.close()
