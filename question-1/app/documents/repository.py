import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from app.documents.models import Document
from app.documents.parsers.base import DocumentParser


class DocumentRepository:
    def __init__(self, data_dir: Path, parser: DocumentParser) -> None:
        self.data_dir = data_dir
        self.parser = parser
        self._documents: Dict[str, Document] = {}

    def load(self) -> None:
        self._documents = {}
        for path in sorted(self.data_dir.glob("*.html")):
            content = path.read_text(encoding="utf-8")
            doc_id = path.stem
            self._documents[doc_id] = self.parser.parse(doc_id, path.name, content)
        self.write_catalog()

    def upsert_html(self, doc_id: str, html: str) -> Document:
        safe_id = self._safe_doc_id(doc_id)
        filename = f"{safe_id}.html"
        path = self.data_dir / filename
        path.write_text(html, encoding="utf-8")
        document = self.parser.parse(safe_id, filename, html)
        self._documents[safe_id] = document
        self.write_catalog()
        return document

    def all(self) -> List[Document]:
        return list(self._documents.values())

    def get(self, doc_id: str) -> Optional[Document]:
        return self._documents.get(doc_id)

    def by_filename(self, filename: str) -> Optional[Document]:
        for document in self._documents.values():
            if document.filename == filename:
                return document
        return None

    def write_catalog(self) -> Path:
        catalog = [
            {
                "id": doc.id,
                "filename": doc.filename,
                "title": doc.title,
                "sections": doc.sections[:12],
                "preview": doc.text[:500],
            }
            for doc in sorted(self._documents.values(), key=lambda item: item.id)
        ]
        path = self.data_dir / "catalog.json"
        path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    @staticmethod
    def _safe_doc_id(doc_id: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", doc_id or ""):
            raise ValueError("document id may only contain letters, numbers, '_' and '-'")
        return doc_id


def index_documents(documents: Iterable[Document]) -> Dict[str, Document]:
    return {document.id: document for document in documents}

