from langchain_openai import OpenAIEmbeddings

from app.infrastructure.graph.neo4j_client import Neo4jClient


class Neo4jVectorStore:
    def __init__(self, neo4j_client: Neo4jClient, embedding_model: str) -> None:
        self.neo4j = neo4j_client
        self.embeddings = OpenAIEmbeddings(model=embedding_model)

    def similarity_search(self, query: str, k: int) -> list[dict]:
        query_vector = self.embeddings.embed_query(query)
        cypher = """
        CALL db.index.vector.queryNodes('chunk_embedding_index', $k, $embedding)
        YIELD node, score
        RETURN node.chunk_id AS chunk_id,
               node.source_doc_id AS source_doc_id,
               node.text AS text,
               score AS vector_score
        """
        return self.neo4j.query(cypher, {"k": k, "embedding": query_vector})
