from app.core.config.settings import get_settings
from app.infrastructure.graph.neo4j_client import Neo4jClient


def main() -> None:
    settings = get_settings()
    neo4j = Neo4jClient(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
        database=settings.neo4j_database,
    )

    queries = [
        "CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.entity_id IS UNIQUE",
        "CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS FOR (c:Chunk) REQUIRE c.chunk_id IS UNIQUE",
        "CREATE CONSTRAINT relates_to_relation_id_unique IF NOT EXISTS FOR ()-[r:RELATES_TO]-() REQUIRE r.relation_id IS UNIQUE",
        "CREATE CONSTRAINT is_a_relation_id_unique IF NOT EXISTS FOR ()-[r:IS_A]-() REQUIRE r.relation_id IS UNIQUE",
        "CREATE CONSTRAINT part_of_relation_id_unique IF NOT EXISTS FOR ()-[r:PART_OF]-() REQUIRE r.relation_id IS UNIQUE",
        "CREATE VECTOR INDEX chunk_embedding_index IF NOT EXISTS FOR (c:Chunk) ON (c.embedding) OPTIONS {indexConfig: {`vector.dimensions`: 1536, `vector.similarity_function`: 'cosine'}}",
        "CREATE INDEX entity_canonical_name IF NOT EXISTS FOR (e:Entity) ON (e.canonical_name)",
    ]

    for q in queries:
        neo4j.query(q)

    neo4j.close()
    print("Neo4j constraints and indexes are ready.")


if __name__ == "__main__":
    main()
