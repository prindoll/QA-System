from dataclasses import dataclass


@dataclass(slots=True)
class RetrievedChunk:
    chunk_id: str
    source_doc_id: str
    text: str
    vector_score: float = 0.0
    lexical_score: float = 0.0
    graph_score: float = 0.0
    final_score: float = 0.0


@dataclass(slots=True)
class GraphFact:
    source_entity_id: str
    relation_type: str
    target_entity_id: str
    confidence: float


@dataclass(slots=True)
class RetrievalBundle:
    chunks: list[RetrievedChunk]
    graph_facts: list[GraphFact]
    graph_paths: list[list[str]]
