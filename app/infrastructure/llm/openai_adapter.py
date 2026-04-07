from openai import AsyncOpenAI

from app.domain.ports.llm_port import LLMPort, LLMRequest


class OpenAIAdapter(LLMPort):
    def __init__(self, api_key: str, model: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(self, request: LLMRequest) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            response_format=request.response_format,
        )
        return response.choices[0].message.content or "{}"
