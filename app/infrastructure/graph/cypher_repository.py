from app.infrastructure.graph.neo4j_client import Neo4jClient


class CypherRepository:
    def __init__(self, neo4j_client: Neo4jClient) -> None:
        self.neo4j = neo4j_client

    def upsert_entities(self, entities: list[dict]) -> None:
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

    def upsert_relationships(self, relationships: list[dict]) -> None:
        cypher = """
        UNWIND $relationships AS rel
        MATCH (s:Entity {entity_id: rel.source_entity_id})
        MATCH (t:Entity {entity_id: rel.target_entity_id})
        MERGE (s)-[r:RELATES_TO {relation_id: rel.relation_id}]->(t)
        ON CREATE SET
          r.predicate = rel.relation_type,
          r.confidence = rel.confidence,
          r.evidence_text = rel.evidence_text,
          r.source_doc_id = rel.source_doc_id,
          r.created_at = datetime()
        ON MATCH SET
          r.confidence = CASE WHEN rel.confidence > coalesce(r.confidence, 0) THEN rel.confidence ELSE r.confidence END,
          r.evidence_text = coalesce(r.evidence_text, rel.evidence_text),
          r.updated_at = datetime()
        """
        self.neo4j.query(cypher, {"relationships": relationships})
