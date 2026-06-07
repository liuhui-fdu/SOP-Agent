from html.parser import HTMLParser
from typing import List

from app.documents.models import Document
from app.documents.parsers.base import DocumentParser
from app.utils.text import normalize_text


class _VisibleTextHTMLParser(HTMLParser):
    _BLOCK_TAGS = {
        "address",
        "article",
        "aside",
        "blockquote",
        "br",
        "div",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "li",
        "main",
        "p",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
        "ol",
    }
    _HIDDEN_TAGS = {"script", "style", "noscript", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: List[str] = []
        self.body_parts: List[str] = []
        self.sections: List[str] = []
        self._tag_stack: List[str] = []
        self._hidden_depth = 0
        self._in_title = False
        self._in_body = False
        self._heading_tag = ""
        self._heading_parts: List[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[override]
        tag = tag.lower()
        self._tag_stack.append(tag)
        if tag in self._HIDDEN_TAGS:
            self._hidden_depth += 1
        if tag == "title":
            self._in_title = True
        if tag == "body":
            self._in_body = True
        if tag in {"h1", "h2", "h3"}:
            self._heading_tag = tag
            self._heading_parts = []
        if tag in self._BLOCK_TAGS and self.body_parts:
            self.body_parts.append(" ")

    def handle_endtag(self, tag: str) -> None:  # type: ignore[override]
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        if tag in {"h1", "h2", "h3"} and self._heading_tag == tag:
            heading = normalize_text("".join(self._heading_parts))
            if heading:
                self.sections.append(heading)
            self._heading_tag = ""
            self._heading_parts = []
        if tag in self._BLOCK_TAGS and self.body_parts:
            self.body_parts.append(" ")
        if tag == "body":
            self._in_body = False
        if tag in self._HIDDEN_TAGS and self._hidden_depth:
            self._hidden_depth -= 1
        if self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:  # type: ignore[override]
        text = normalize_text(data)
        if not text:
            return
        if self._in_title:
            self.title_parts.append(text)
        if self._hidden_depth:
            return
        if self._in_body:
            self.body_parts.append(text)
            self.body_parts.append(" ")
            if self._heading_tag:
                self._heading_parts.append(text)


class HtmlDocumentParser(DocumentParser):
    name = "html"

    def parse(self, doc_id: str, filename: str, content: str) -> Document:
        parser = _VisibleTextHTMLParser()
        parser.feed(content)
        title = normalize_text(" ".join(parser.title_parts))
        text = normalize_text(" ".join(parser.body_parts))
        if not title and parser.sections:
            title = parser.sections[0]
        if not title:
            title = doc_id
        return Document(
            id=doc_id,
            filename=filename,
            title=title,
            text=text,
            sections=parser.sections,
            metadata={"parser": self.name},
        )

