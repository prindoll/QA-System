from dataclasses import dataclass, field


@dataclass(slots=True)
class Relation:
    relation_id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: str
    confidence: float
    evidence_text: str
    attributes: dict = field(default_factory=dict)
    source_doc_id: str = ""
