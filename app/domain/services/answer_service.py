import json

from app.api.schemas.response import Citation, QAResponse
from app.domain.ports.llm_port import LLMPort, LLMRequest
from app.domain.services.retrieval_service import RetrievalService


SYSTEM_PROMPT = """
Bạn là trợ lý QA theo nguyên tắc grounded-answering.
Chỉ được phép dựa trên context đã cung cấp.
Nếu không đủ bằng chứng, trả lời rõ là không đủ dữ liệu.
Bắt buộc trả về JSON với schema:
{
  "answer": "string",
  "confidence": 0.0-1.0,
  "citations": [{"chunk_id": "...", "source_doc_id": "..."}]
}
""".strip()


class AnswerService:
    def __init__(self, llm: LLMPort, retrieval_service: RetrievalService) -> None:
        self.llm = llm
        self.retrieval_service = retrieval_service

    async def answer(self, query: str, top_k: int, max_hops: int) -> QAResponse:
        bundle = self.retrieval_service.retrieve(query=query, top_k=top_k, max_hops=max_hops)

        chunk_context = "\n\n".join(
            [
                f"[chunk_id={item.chunk_id} doc_id={item.source_doc_id} score={item.final_score:.3f}]\n{item.text}"
                for item in bundle.chunks
            ]
        )
        graph_context = "\n".join(
            [
                f"{f.source_entity_id} -[{f.relation_type}:{f.confidence:.2f}]-> {f.target_entity_id}"
                for f in bundle.graph_facts
            ]
        )

        user_prompt = f"""
Question: {query}

Retrieved documents:
{chunk_context}

Graph facts:
{graph_context}

Graph paths:
{json.dumps(bundle.graph_paths, ensure_ascii=True)}

Hãy trả lời ngắn gọn, rõ ràng, đúng theo context.
""".strip()

        raw = await self.llm.generate(
            LLMRequest(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.0,
                response_format={"type": "json_object"},
            )
        )

        payload = json.loads(raw)
        citations = [Citation(**c) for c in payload.get("citations", [])]

        return QAResponse(
            answer=payload.get("answer", "Không đủ dữ liệu để trả lời."),
            confidence=float(payload.get("confidence", 0.0)),
            citations=citations,
            used_graph_paths=bundle.graph_paths,
        )
