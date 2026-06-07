from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class Document:
    id: str
    filename: str
    title: str
    text: str
    sections: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

