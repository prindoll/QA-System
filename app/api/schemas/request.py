from pydantic import BaseModel, Field


class QARequest(BaseModel):
    query: str = Field(min_length=2)
    top_k: int = Field(default=12, ge=3, le=30)
    max_hops: int = Field(default=2, ge=1, le=4)
