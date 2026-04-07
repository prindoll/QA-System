from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: str
    source_doc_id: str


class QAResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    citations: list[Citation]
    used_graph_paths: list[list[str]]
