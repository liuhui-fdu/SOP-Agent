from collections import Counter
from typing import Dict, List, Optional

from app.documents.models import Document
from app.search.base import SearchProvider
from app.search.models import SearchResult
from app.search.scoring import coverage_score
from app.search.snippets import make_snippet
from app.utils.text import lower_text, tokenize


class KeywordSearchProvider(SearchProvider):
    name = "keyword"

    def __init__(self, documents: List[Document], top_k: int = 10) -> None:
        self.documents = documents
        self.top_k = top_k
        self._tokens: Dict[str, Counter] = {
            doc.id: Counter(tokenize(f"{doc.title} {doc.text}")) for doc in documents
        }
        self._text_terms: Dict[str, set] = {
            doc.id: set(self._tokens[doc.id]) for doc in documents
        }

    def search(self, query: str, limit: Optional[int] = None) -> List[SearchResult]:
        limit = limit or self.top_k
        query_lower = lower_text(query)
        if not query_lower:
            return []

        query_tokens = tokenize(query_lower)
        results: List[SearchResult] = []
        for document in self.documents:
            haystack = lower_text(f"{document.title} {document.text}")
            exact_hits = haystack.count(query_lower)
            token_hits = sum(self._tokens[document.id].get(token, 0) for token in query_tokens)
            coverage = coverage_score(query_tokens, self._text_terms[document.id])
            score = exact_hits * 5.0 + token_hits * 0.35 + coverage
            if score > 0:
                results.append(
                    SearchResult(
                        id=document.id,
                        title=document.title,
                        snippet=make_snippet(document, query),
                        score=score,
                    )
                )
        results.sort(key=lambda item: (-item.score, item.id))
        return results[:limit]
