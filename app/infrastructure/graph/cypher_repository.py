import hashlib

from app.infrastructure.graph.neo4j_client import Neo4jClient


class CypherRepository:
    RELATION_TYPES = ("IS_A", "PART_OF", "RELATES_TO")

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        self.neo4j = neo4j_client

    def upsert_entities(self, entities: list[dict]) -> None:
        if not entities:
            return
        cypher = """
        UNWIND $entities AS ent
        MERGE (e:Entity {entity_id: ent.entity_id})
        ON CREATE SET
          e.canonical_name = ent.canonical_name,
          e.entity_type = ent.entity_type,
          e.aliases = coalesce(ent.aliases, []),
          e.attributes = coalesce(ent.attributes, {}),
          e.created_at = datetime()
        ON MATCH SET
          e.canonical_name = coalesce(e.canonical_name, ent.canonical_name),
          e.entity_type = coalesce(e.entity_type, ent.entity_type),
          e.aliases = apoc.coll.toSet(coalesce(e.aliases, []) + coalesce(ent.aliases, [])),
          e.attributes = coalesce(e.attributes, {}) + coalesce(ent.attributes, {}),
          e.updated_at = datetime()
        """
        self.neo4j.query(cypher, {"entities": entities})

    def upsert_mentions(
        self,
        entities: list[dict],
        chunk_id: str,
        source_doc_id: str,
        chunk_text: str,
    ) -> None:
        rows = [ent for ent in entities if ent.get("entity_id")]
        if not rows:
            return

        cypher = """
        UNWIND $entities AS ent
        MATCH (e:Entity {entity_id: ent.entity_id})
        MERGE (c:Chunk {chunk_id: $chunk_id})
        ON CREATE SET
          c.source_doc_id = $source_doc_id,
          c.text = $chunk_text,
          c.created_at = datetime()
        ON MATCH SET
          c.source_doc_id = coalesce(c.source_doc_id, $source_doc_id),
          c.text = coalesce(c.text, $chunk_text),
          c.updated_at = datetime()
        MERGE (e)-[m:MENTIONED_IN]->(c)
        ON CREATE SET
          m.source_doc_id = $source_doc_id,
          m.created_at = datetime()
        ON MATCH SET
          m.source_doc_id = coalesce(m.source_doc_id, $source_doc_id),
          m.updated_at = datetime()
        """
        self.neo4j.query(
            cypher,
            {
                "entities": rows,
                "chunk_id": chunk_id,
                "source_doc_id": source_doc_id,
                "chunk_text": chunk_text,
            },
        )

    def upsert_relationships(self, relationships: list[dict]) -> None:
        normalized = [self._normalize_relationship(rel) for rel in relationships]
        normalized = [rel for rel in normalized if rel]
        if not normalized:
            return

        for rel_type in self.RELATION_TYPES:
            rows = [rel for rel in normalized if rel["relation_type"] == rel_type]
            if not rows:
                continue

            self.neo4j.query(
                self._build_upsert_relationships_cypher(rel_type=rel_type),
                {"relationships": rows},
            )

    def _normalize_relationship(self, rel: dict) -> dict:
        source_entity_id = str(rel.get("source_entity_id") or "").strip()
        target_entity_id = str(rel.get("target_entity_id") or "").strip()
        if not source_entity_id or not target_entity_id:
            return {}

        relation_type = str(rel.get("relation_type") or "RELATES_TO").strip().upper()
        if relation_type not in self.RELATION_TYPES:
            relation_type = "RELATES_TO"

        relation_id = str(rel.get("relation_id") or "").strip()
        if not relation_id:
            relation_id = self._make_relation_id(
                source_entity_id=source_entity_id,
                relation_type=relation_type,
                target_entity_id=target_entity_id,
            )

        return {
            "relation_id": relation_id,
            "source_entity_id": source_entity_id,
            "target_entity_id": target_entity_id,
            "relation_type": relation_type,
            "confidence": self._parse_confidence(rel.get("confidence")),
            "evidence_text": str(rel.get("evidence_text") or ""),
            "source_doc_id": str(rel.get("source_doc_id") or ""),
            "source_chunk_id": str(rel.get("source_chunk_id") or ""),
        }

    def _build_upsert_relationships_cypher(self, rel_type: str) -> str:
        cypher = """
        UNWIND $relationships AS rel
        MATCH (s:Entity {entity_id: rel.source_entity_id})
        MATCH (t:Entity {entity_id: rel.target_entity_id})
        MERGE (s)-[r:%s {relation_id: rel.relation_id}]->(t)
        ON CREATE SET
          r.predicate = rel.relation_type,
          r.confidence = rel.confidence,
          r.evidence_text = rel.evidence_text,
          r.source_doc_id = rel.source_doc_id,
          r.source_chunk_id = rel.source_chunk_id,
          r.created_at = datetime()
        ON MATCH SET
          r.confidence = CASE WHEN rel.confidence > coalesce(r.confidence, 0) THEN rel.confidence ELSE r.confidence END,
          r.evidence_text = coalesce(r.evidence_text, rel.evidence_text),
          r.source_doc_id = coalesce(r.source_doc_id, rel.source_doc_id),
          r.source_chunk_id = coalesce(r.source_chunk_id, rel.source_chunk_id),
          r.updated_at = datetime()
        """ % rel_type
        return cypher

    def _make_relation_id(self, source_entity_id: str, relation_type: str, target_entity_id: str) -> str:
        key = "::".join([source_entity_id, relation_type, target_entity_id])
        return "rel_" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]

    def _parse_confidence(self, value: object) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
