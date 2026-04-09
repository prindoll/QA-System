import asyncio

from app.core.config.settings import get_settings
from app.infrastructure.graph.cypher_repository import CypherRepository
from app.infrastructure.graph.neo4j_client import Neo4jClient
from app.infrastructure.ingestion.chunking.semantic_chunker import SemanticChunker
from app.infrastructure.llm.factory import LLMFactory
from app.processing.extraction.extractor import ExtractionEngine
from app.processing.indexing.graph_indexer import GraphIndexer
from app.processing.indexing.vector_indexer import VectorIndexer
from app.processing.normalize.entity_resolver import EntityResolver
from app.processing.normalize.ontology_mapper import OntologyMapper


async def ingest_document(text: str, doc_id: str) -> None:
    settings = get_settings()
    llm = LLMFactory.create_from_settings(settings)

    neo4j = Neo4jClient(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
        database=settings.neo4j_database,
    )

    extractor = ExtractionEngine(llm=llm)
    mapper = OntologyMapper()
    resolver = EntityResolver()
    repo = CypherRepository(neo4j_client=neo4j)
    graph_indexer = GraphIndexer(repo=repo)
    vector_indexer = VectorIndexer(neo4j_client=neo4j, embedding_model=settings.openai_embedding_model)
    chunker = SemanticChunker()

    chunks = chunker.split(text=text, doc_id=doc_id)
    for chunk in chunks:
        extracted = await extractor.extract(
            text=chunk["text"],
            doc_id=doc_id,
            chunk_id=chunk["chunk_id"],
        )
        normalized = resolver.resolve_payload(mapper.map_payload(extracted))
        graph_indexer.index(
            normalized_payload=normalized,
            chunk_id=chunk["chunk_id"],
            source_doc_id=doc_id,
            chunk_text=chunk["text"],
        )

    vector_indexer.index_chunks(chunks)
    neo4j.close()


def run_ingest(text: str, doc_id: str) -> None:
    asyncio.run(ingest_document(text=text, doc_id=doc_id))
