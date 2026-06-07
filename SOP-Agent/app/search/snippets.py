from app.documents.models import Document
from app.utils.text import lower_text, normalize_text


def make_snippet(document: Document, query: str, limit: int = 150) -> str:
    text = normalize_text(document.text)
    lowered = lower_text(text)
    query_lower = lower_text(query)
    start = 0
    if query_lower:
        found = lowered.find(query_lower)
        if found >= 0:
            start = max(0, found - 45)
    snippet = text[start : start + limit].strip()
    if start > 0:
        snippet = "..." + snippet
    if start + limit < len(text):
        snippet += "..."
    return snippet

