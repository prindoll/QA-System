from dataclasses import dataclass


@dataclass(slots=True)
class DocumentChunk:
    chunk_id: str
    doc_id: str
    text: str
    section: str | None = None
