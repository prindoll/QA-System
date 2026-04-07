from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.schemas.request import QARequest
from app.api.schemas.response import QAResponse
from app.dependencies import get_answer_service
from app.domain.services.answer_service import AnswerService

router = APIRouter()


@router.post("/ask")
async def ask_question(
    payload: QARequest,
    answer_service: Annotated[AnswerService, Depends(get_answer_service)],
) -> QAResponse:
    return await answer_service.answer(
        query=payload.query,
        top_k=payload.top_k,
        max_hops=payload.max_hops,
    )
