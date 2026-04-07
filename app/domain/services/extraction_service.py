from app.processing.extraction.extractor import ExtractionEngine


class ExtractionService:
    def __init__(self, engine: ExtractionEngine) -> None:
        self.engine = engine

    async def run(self, text: str, doc_id: str, chunk_id: str) -> dict:
        return await self.engine.extract(text=text, doc_id=doc_id, chunk_id=chunk_id)
