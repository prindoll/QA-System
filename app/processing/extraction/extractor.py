import json

from app.domain.ports.llm_port import LLMPort, LLMRequest
from app.processing.extraction.prompts import EXTRACTION_SYSTEM_PROMPT, build_extraction_user_prompt


class ExtractionEngine:
    def __init__(self, llm: LLMPort) -> None:
        self.llm = llm

    async def extract(self, text: str, doc_id: str, chunk_id: str) -> dict:
        prompt = build_extraction_user_prompt(text=text, doc_id=doc_id, chunk_id=chunk_id)
        raw = await self.llm.generate(
            LLMRequest(
                system_prompt=EXTRACTION_SYSTEM_PROMPT,
                user_prompt=prompt,
                temperature=0.0,
                response_format={"type": "json_object"},
                max_tokens=1800,
            )
        )
        return json.loads(raw)
