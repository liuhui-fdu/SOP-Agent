from dataclasses import dataclass


@dataclass(frozen=True)
class SearchResult:
    id: str
    title: str
    snippet: str
    score: float

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "snippet": self.snippet,
            "score": round(self.score, 4),
        }

