from app.processing.normalize.ontology_mapper import OntologyMapper


def test_ontology_mapper_maps_entity_and_relation() -> None:
    mapper = OntologyMapper()
    payload = {
        "entities": [{"entity_type": "company"}],
        "relationships": [{"relation_type": "is-a"}],
    }

    mapped = mapper.map_payload(payload)
    assert mapped["entities"][0]["entity_type"] == "Organization"
    assert mapped["relationships"][0]["relation_type"] == "IS_A"
