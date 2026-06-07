from typing import Dict, List, Optional

from app.search.base import SearchProvider
from app.search.models import SearchResult


class HybridSearchProvider(SearchProvider):
    name = "hybrid"

    def __init__(
        self,
        keyword_provider: SearchProvider,
        semantic_provider: SearchProvider,
        keyword_weight: float = 1.0,
        semantic_weight: float = 1.0,
    ) -> None:
        self.keyword_provider = keyword_provider
        self.semantic_provider = semantic_provider
        self.keyword_weight = keyword_weight
        self.semantic_weight = semantic_weight

    def search(self, query: str, limit: Optional[int] = None) -> List[SearchResult]:
        merged: Dict[str, SearchResult] = {}
        for result in self.keyword_provider.search(query, limit):
            merged[result.id] = SearchResult(
                id=result.id,
                title=result.title,
                snippet=result.snippet,
                score=result.score * self.keyword_weight,
            )
        for result in self.semantic_provider.search(query, limit):
            existing = merged.get(result.id)
            score = result.score * self.semantic_weight
            if existing:
                merged[result.id] = SearchResult(
                    id=result.id,
                    title=result.title,
                    snippet=existing.snippet,
                    score=existing.score + score,
                )
            else:
                merged[result.id] = SearchResult(
                    id=result.id,
                    title=result.title,
                    snippet=result.snippet,
                    score=score,
                )
        results = list(merged.values())
        results.sort(key=lambda item: (-item.score, item.id))
        return results[:limit] if limit else results
