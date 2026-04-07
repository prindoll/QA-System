from app.core.config.settings import Settings
from app.infrastructure.llm.local_vllm_adapter import LocalVLLMAdapter
from app.infrastructure.llm.openai_adapter import OpenAIAdapter


class LLMFactory:
    @staticmethod
    def create_from_settings(settings: Settings):
        if settings.llm_provider == "openai":
            return OpenAIAdapter(
                api_key=settings.openai_api_key,
                model=settings.openai_chat_model,
            )
        if settings.llm_provider == "local_vllm":
            return LocalVLLMAdapter(endpoint="http://localhost:8001", model=settings.openai_chat_model)
        msg = f"Unsupported llm provider: {settings.llm_provider}"
        raise ValueError(msg)
