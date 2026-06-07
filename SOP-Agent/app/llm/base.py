from abc import ABC, abstractmethod
from typing import Sequence


class LLMClient(ABC):
    provider: str

    @abstractmethod
    def complete(self, system_prompt: str, messages: Sequence[dict]) -> str:
        raise NotImplementedError

