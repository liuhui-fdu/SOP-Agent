from collections import Counter
from typing import Dict, List, Optional

from app.documents.models import Document
from app.search.base import SearchProvider
from app.search.models import SearchResult
from app.search.scoring import cosine_from_counters
from app.search.snippets import make_snippet
from app.utils.text import tokenize, unique_preserve_order


class SemanticSearchProvider(SearchProvider):
    name = "semantic"

    def __init__(
        self,
        documents: List[Document],
        concepts: Dict[str, List[str]],
        top_k: int = 10,
    ) -> None:
        self.documents = documents
        self.concepts = concepts
        self.top_k = top_k
        self._doc_vectors = {
            document.id: Counter(tokenize(self._expand_text(f"{document.title} {document.text}")))
            for document in documents
        }

    def search(self, query: str, limit: Optional[int] = None) -> List[SearchResult]:
        limit = limit or self.top_k
        expanded_query = self._expand_text(query)
        query_vector = Counter(tokenize(expanded_query))
        if not query_vector:
            return []

        results: List[SearchResult] = []
        for document in self.documents:
            score = cosine_from_counters(query_vector, self._doc_vectors[document.id])
            concept_bonus = self._concept_bonus(query, document)
            final_score = score + concept_bonus
            if final_score > 0:
                results.append(
                    SearchResult(
                        id=document.id,
                        title=document.title,
                        snippet=make_snippet(document, query),
                        score=final_score,
                    )
                )
        results.sort(key=lambda item: (-item.score, item.id))
        return results[:limit]

    def _expand_text(self, text: str) -> str:
        additions: List[str] = [text]
        text_tokens = set(tokenize(text))
        lowered = text.lower()
        for concept, terms in self.concepts.items():
            concept_tokens = set(tokenize(" ".join([concept] + terms)))
            if concept in lowered or text_tokens & concept_tokens:
                additions.extend(terms)
        return " ".join(unique_preserve_order(additions))

    def _concept_bonus(self, query: str, document: Document) -> float:
        query_expanded = set(tokenize(self._expand_text(query)))
        doc_expanded = set(tokenize(self._expand_text(f"{document.title} {document.text}")))
        shared = query_expanded & doc_expanded
        if not query_expanded:
            return 0.0
        return min(0.4, len(shared) / len(query_expanded) * 0.2)
