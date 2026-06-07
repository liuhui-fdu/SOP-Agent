import json
import os
import urllib.request
from typing import Sequence

from app.llm.base import LLMClient


class OpenAILLMClient(LLMClient):
    provider = "openai"

    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY", "")

    def complete(self, system_prompt: str, messages: Sequence[dict]) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}] + list(messages),
        }
        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]

