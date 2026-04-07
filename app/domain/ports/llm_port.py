from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class LLMRequest:
    system_prompt: str
    user_prompt: str
    temperature: float = 0.0
    max_tokens: int = 1200
    response_format: dict[str, Any] | None = None


class LLMPort(ABC):
    @abstractmethod
    async def generate(self, request: LLMRequest) -> str:
        raise NotImplementedError
