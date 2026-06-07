import json
import os
import urllib.request
from typing import Sequence
from typing import Optional

from app.llm.base import LLMClient


class CodeFuseLLMClient(LLMClient):
    provider = "codefuse"

    def __init__(self, endpoint: Optional[str] = None, model: str = "codefuse") -> None:
        self.endpoint = endpoint or os.getenv("CODEFUSE_API_BASE", "")
        self.api_key = os.getenv("CODEFUSE_API_KEY", "")
        self.model = os.getenv("CODEFUSE_MODEL", model)

    def complete(self, system_prompt: str, messages: Sequence[dict]) -> str:
        if not self.endpoint or not self.api_key:
            raise RuntimeError("CODEFUSE_API_BASE and CODEFUSE_API_KEY are required")
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}] + list(messages),
        }
        request = urllib.request.Request(
            self.endpoint.rstrip("/") + "/chat/completions",
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
