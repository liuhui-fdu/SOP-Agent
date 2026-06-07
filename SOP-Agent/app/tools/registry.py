from typing import Dict, Iterable

from app.tools.base import Tool


class ToolRegistry:
    def __init__(self, tools: Iterable[Tool]) -> None:
        self._tools: Dict[str, Tool] = {tool.name: tool for tool in tools}

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"tool not registered: {name}")
        return self._tools[name]

    def names(self) -> list[str]:
        return sorted(self._tools)

