from typing import Sequence

from app.llm.base import LLMClient


class MockLLMClient(LLMClient):
    provider = "mock"

    def complete(self, system_prompt: str, messages: Sequence[dict]) -> str:
        if messages:
            return str(messages[-1].get("content", ""))
        return ""

