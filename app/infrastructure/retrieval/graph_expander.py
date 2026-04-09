from app.domain.models.retrieval import GraphFact, RetrievalBundle
from app.infrastructure.graph.neo4j_client import Neo4jClient


class GraphExpander:
    def __init__(
        self,
        neo4j_client: Neo4jClient,
        max_hops: int = 2,
        neighbor_limit: int = 8,
        relevance_threshold: float = 0.45,
    ) -> None:
        self.neo4j = neo4j_client
        self.max_hops = max_hops
        self.neighbor_limit = neighbor_limit
        self.relevance_threshold = relevance_threshold

    def expand(self, seed_bundle: RetrievalBundle, max_hops: int | None = None) -> RetrievalBundle:
        hops = max_hops or self.max_hops
        if not seed_bundle.chunks:
            return seed_bundle

        chunk_ids = [c.chunk_id for c in seed_bundle.chunks]
        rows = self._expand_from_chunks(chunk_ids=chunk_ids, max_hops=hops)

        graph_facts: list[GraphFact] = []
        graph_paths: list[list[str]] = []

        for row in rows:
            confidence = float(row.get("confidence", 0.0))
            if confidence < self.relevance_threshold:
                continue
            graph_facts.append(
                GraphFact(
                    source_entity_id=row["source_id"],
                    relation_type=row["relation"],
                    target_entity_id=row["target_id"],
                    confidence=confidence,
                )
            )
            graph_paths.append(row.get("path", []))

        seed_bundle.graph_facts = graph_facts
        seed_bundle.graph_paths = graph_paths
        return seed_bundle

    def _expand_from_chunks(self, chunk_ids: list[str], max_hops: int) -> list[dict]:
        cypher = """
        MATCH (c:Chunk)
        WHERE c.chunk_id IN $chunk_ids
        MATCH (c)<-[:MENTIONED_IN]-(seed:Entity)
        CALL {
          WITH seed
          MATCH p=(seed)-[r:RELATES_TO|IS_A|PART_OF*1..$max_hops]->(n:Entity)
          WITH p, relationships(p) AS rs
          RETURN
            head(nodes(p)).entity_id AS source_id,
            last(nodes(p)).entity_id AS target_id,
            type(last(rs)) AS relation,
            reduce(acc = 1.0, x IN rs | acc * coalesce(x.confidence, 0.7)) AS confidence,
            [node IN nodes(p) | node.entity_id] AS path
          LIMIT $neighbor_limit
        }
        RETURN source_id, target_id, relation, confidence, path
        """
        return self.neo4j.query(
            cypher,
            {
                "chunk_ids": chunk_ids,
                "max_hops": max_hops,
                "neighbor_limit": self.neighbor_limit,
            },
        )
