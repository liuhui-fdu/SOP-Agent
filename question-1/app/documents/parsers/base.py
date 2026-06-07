from abc import ABC, abstractmethod

from app.documents.models import Document


class DocumentParser(ABC):
    name: str

    @abstractmethod
    def parse(self, doc_id: str, filename: str, content: str) -> Document:
        raise NotImplementedError

