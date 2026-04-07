from app.processing.normalize.entity_resolver import EntityResolver


def test_entity_resolver_deduplicates_entities() -> None:
    resolver = EntityResolver()
    payload = {
        "entities": [
            {"canonical_name": "Product A", "entity_type": "Product"},
            {"canonical_name": "Product A", "entity_type": "Product"},
        ],
        "relationships": [],
    }

    result = resolver.resolve_payload(payload)
    assert len(result["entities"]) == 1
    assert result["entities"][0]["entity_id"].startswith("ent_")
