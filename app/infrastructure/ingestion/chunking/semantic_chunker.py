import hashlib


class SemanticChunker:
    def __init__(self, chunk_size: int = 1200, overlap: int = 150) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, text: str, doc_id: str) -> list[dict]:
        chunks: list[dict] = []
        start = 0
        n = len(text)

        while start < n:
            end = min(start + self.chunk_size, n)
            content = text[start:end].strip()
            if content:
                digest = hashlib.sha1(f"{doc_id}:{start}:{content}".encode("utf-8")).hexdigest()[:12]
                chunks.append(
                    {
                        "chunk_id": f"chk_{digest}",
                        "source_doc_id": doc_id,
                        "text": content,
                    }
                )
            if end == n:
                break
            start = max(0, end - self.overlap)

        return chunks
