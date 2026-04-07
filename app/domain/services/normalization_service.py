from app.processing.normalize.entity_resolver import EntityResolver
from app.processing.normalize.ontology_mapper import OntologyMapper


class NormalizationService:
    def __init__(self, ontology_mapper: OntologyMapper, entity_resolver: EntityResolver) -> None:
        self.ontology_mapper = ontology_mapper
        self.entity_resolver = entity_resolver

    def run(self, extraction_output: dict) -> dict:
        mapped = self.ontology_mapper.map_payload(extraction_output)
        return self.entity_resolver.resolve_payload(mapped)
