from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "GraphRAG QA"
    app_env: str = "dev"
    app_port: int = 8000

    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    llm_provider: str = "openai"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4jpassword"
    neo4j_database: str = "neo4j"

    retrieval_top_k: int = 12
    graph_max_hops: int = 2
    graph_neighbor_limit: int = 8
    graph_relevance_threshold: float = 0.45


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
