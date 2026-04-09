from pydantic import BaseModel, Field


class ExtractedEntity(BaseModel):
    entity_id: str
    canonical_name: str
    entity_type: str
    aliases: list[str] = Field(default_factory=list)
    attributes: dict = Field(default_factory=dict)
    confidence: float


class ExtractedRelation(BaseModel):
    relation_id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: str
    confidence: float
    evidence_text: str
    source_doc_id: str
    source_chunk_id: str


class ExtractionOutput(BaseModel):
    entities: list[ExtractedEntity] = Field(default_factory=list)
    relationships: list[ExtractedRelation] = Field(default_factory=list)
    multi_hop_paths: list[list[str]] = Field(default_factory=list)
    source_doc_id: str
    source_chunk_id: str
