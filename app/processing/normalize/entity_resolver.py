import hashlib


class EntityResolver:
    def resolve_payload(self, payload: dict) -> dict:
        entities = payload.get("entities", [])

        canonical_index: dict[str, str] = {}
        deduped_entities: list[dict] = []

        for ent in entities:
            key = self._entity_key(ent)
            if key in canonical_index:
                continue

            entity_id = ent.get("entity_id") or self._make_entity_id(key)
            canonical_index[key] = entity_id
            ent["entity_id"] = entity_id
            deduped_entities.append(ent)

        payload["entities"] = deduped_entities

        for rel in payload.get("relationships", []):
            src = rel.get("source_entity_id", "")
            tgt = rel.get("target_entity_id", "")
            rel["source_entity_id"] = self._resolve_entity_ref(src, deduped_entities)
            rel["target_entity_id"] = self._resolve_entity_ref(tgt, deduped_entities)
            if not rel.get("relation_id"):
                rel["relation_id"] = self._make_relation_id(rel)

        return payload

    def _entity_key(self, ent: dict) -> str:
        name = str(ent.get("canonical_name", "")).strip().lower()
        etype = str(ent.get("entity_type", "Concept")).strip().lower()
        return f"{name}::{etype}"

    def _make_entity_id(self, key: str) -> str:
        return "ent_" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]

    def _make_relation_id(self, rel: dict) -> str:
        key = "::".join(
            [
                str(rel.get("source_entity_id", "")),
                str(rel.get("relation_type", "RELATES_TO")),
                str(rel.get("target_entity_id", "")),
            ]
        )
        return "rel_" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]

    def _resolve_entity_ref(self, raw_ref: str, entities: list[dict]) -> str:
        for ent in entities:
            if raw_ref in {ent.get("entity_id"), ent.get("canonical_name")}:
                return ent["entity_id"]
        return raw_ref
