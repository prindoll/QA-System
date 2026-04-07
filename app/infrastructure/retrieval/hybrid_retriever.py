from app.domain.models.retrieval import RetrievalBundle, RetrievedChunk
from app.infrastructure.graph.neo4j_client import Neo4jClient
from app.infrastructure.vector.neo4j_vector_store import Neo4jVectorStore


class HybridRetriever:
    def __init__(self, vector_store: Neo4jVectorStore, neo4j_client: Neo4jClient, top_k: int = 12) -> None:
        self.vector_store = vector_store
        self.neo4j = neo4j_client
        self.top_k = top_k

    def retrieve(self, query: str, top_k: int | None = None) -> RetrievalBundle:
        k = top_k or self.top_k
        vector_hits = self.vector_store.similarity_search(query=query, k=k)
        graph_hits = self._graph_seed_search(query=query, k=k)

        fused = self._fuse_scores(vector_hits, graph_hits)
        ranked = sorted(fused.values(), key=lambda x: x.final_score, reverse=True)

        return RetrievalBundle(chunks=ranked[:k], graph_facts=[], graph_paths=[])

    def _graph_seed_search(self, query: str, k: int) -> list[dict]:
        cypher = """
        MATCH (e:Entity)-[:MENTIONED_IN]->(c:Chunk)
        WHERE toLower(e.canonical_name) CONTAINS toLower($query)
        RETURN c.chunk_id AS chunk_id,
               c.source_doc_id AS source_doc_id,
               c.text AS text,
               0.70 AS graph_score
        LIMIT $k
        """
        return self.neo4j.query(cypher, {"query": query, "k": k})

    def _fuse_scores(self, vector_hits: list[dict], graph_hits: list[dict]) -> dict[str, RetrievedChunk]:
        alpha, gamma = 0.7, 0.3
        bucket: dict[str, RetrievedChunk] = {}

        for hit in vector_hits:
            item = bucket.get(hit["chunk_id"])
            if not item:
                item = RetrievedChunk(
                    chunk_id=hit["chunk_id"],
                    source_doc_id=hit.get("source_doc_id", ""),
                    text=hit.get("text", ""),
                )
                bucket[item.chunk_id] = item
            item.vector_score = float(hit.get("vector_score", 0.0))
            item.final_score += alpha * item.vector_score

        for hit in graph_hits:
            item = bucket.get(hit["chunk_id"])
            if not item:
                item = RetrievedChunk(
                    chunk_id=hit["chunk_id"],
                    source_doc_id=hit.get("source_doc_id", ""),
                    text=hit.get("text", ""),
                )
                bucket[item.chunk_id] = item
            item.graph_score = float(hit.get("graph_score", 0.0))
            item.final_score += gamma * item.graph_score

        return bucket
