from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: Dict[str, str]
    result_preview: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "arguments": self.arguments,
            "result_preview": self.result_preview,
        }


@dataclass(frozen=True)
class AgentResponse:
    answer: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "tool_calls": [call.to_dict() for call in self.tool_calls],
            "sources": self.sources,
        }

