class OntologyMapper:
    TYPE_MAP = {
        "person": "Person",
        "organization": "Organization",
        "company": "Organization",
        "product": "Product",
        "concept": "Concept",
    }

    RELATION_MAP = {
        "is-a": "IS_A",
        "is_a": "IS_A",
        "part-of": "PART_OF",
        "part_of": "PART_OF",
        "related_to": "RELATES_TO",
        "relates_to": "RELATES_TO",
    }
    ALLOWED_RELATION_TYPES = {"IS_A", "PART_OF", "RELATES_TO"}

    def map_payload(self, payload: dict) -> dict:
        for ent in payload.get("entities", []):
            raw_type = str(ent.get("entity_type", "Concept")).lower()
            ent["entity_type"] = self.TYPE_MAP.get(raw_type, ent.get("entity_type", "Concept"))

        for rel in payload.get("relationships", []):
            raw_rel = str(rel.get("relation_type", "RELATES_TO")).lower()
            mapped = self.RELATION_MAP.get(raw_rel, str(rel.get("relation_type", "RELATES_TO")).upper())
            rel["relation_type"] = mapped if mapped in self.ALLOWED_RELATION_TYPES else "RELATES_TO"

        return payload
