from functools import lru_cache

from app.core.config.settings import get_settings
from app.domain.services.answer_service import AnswerService
from app.domain.services.retrieval_service import RetrievalService
from app.infrastructure.graph.neo4j_client import Neo4jClient
from app.infrastructure.llm.factory import LLMFactory
from app.infrastructure.retrieval.graph_expander import GraphExpander
from app.infrastructure.retrieval.hybrid_retriever import HybridRetriever
from app.infrastructure.vector.neo4j_vector_store import Neo4jVectorStore


@lru_cache(maxsize=1)
def get_neo4j_client() -> Neo4jClient:
    settings = get_settings()
    return Neo4jClient(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
        database=settings.neo4j_database,
    )


@lru_cache(maxsize=1)
def get_llm_adapter():
    settings = get_settings()
    return LLMFactory.create_from_settings(settings)


@lru_cache(maxsize=1)
def get_vector_store() -> Neo4jVectorStore:
    settings = get_settings()
    return Neo4jVectorStore(
        neo4j_client=get_neo4j_client(),
        embedding_model=settings.openai_embedding_model,
    )


@lru_cache(maxsize=1)
def get_hybrid_retriever() -> HybridRetriever:
    settings = get_settings()
    return HybridRetriever(
        vector_store=get_vector_store(),
        neo4j_client=get_neo4j_client(),
        top_k=settings.retrieval_top_k,
    )


@lru_cache(maxsize=1)
def get_retrieval_service() -> RetrievalService:
    settings = get_settings()
    graph_expander = GraphExpander(
        neo4j_client=get_neo4j_client(),
        max_hops=settings.graph_max_hops,
        neighbor_limit=settings.graph_neighbor_limit,
        relevance_threshold=settings.graph_relevance_threshold,
    )
    return RetrievalService(
        hybrid_retriever=get_hybrid_retriever(),
        graph_expander=graph_expander,
    )


@lru_cache(maxsize=1)
def get_answer_service() -> AnswerService:
    return AnswerService(
        llm=get_llm_adapter(),
        retrieval_service=get_retrieval_service(),
    )
