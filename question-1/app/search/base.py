from abc import ABC, abstractmethod
from typing import List, Optional

from app.search.models import SearchResult


class SearchProvider(ABC):
    name: str

    @abstractmethod
    def search(self, query: str, limit: Optional[int] = None) -> List[SearchResult]:
        raise NotImplementedError
