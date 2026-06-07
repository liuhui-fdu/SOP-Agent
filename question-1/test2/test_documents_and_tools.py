import tempfile
import unittest
from pathlib import Path

from app.documents.parsers.html_parser import HtmlDocumentParser
from app.documents.repository import DocumentRepository
from app.tools.read_file import ReadFileTool
from app.tools.registry import ToolRegistry


class DocumentsAndToolsExtendedTest(unittest.TestCase):
    def test_html_parser_sections_entities_and_hidden_content(self) -> None:
        html = """
        <html><head><title>前端Web On&#45;Call SOP &amp; 指南</title>
        <style>.secret{content:'CDN'}</style></head>
        <body><header><h1>前端Web On&#45;Call SOP</h1></header>
        <main><h2>一&#12289;处理</h2><p>PC端&#38;移动端H5&#38;小程序WebView</p></main>
        <script>replication</script></body></html>
        """
        doc = HtmlDocumentParser().parse("sop-x", "sop-x.html", html)
        self.assertEqual("前端Web On-Call SOP & 指南", doc.title)
        self.assertIn("PC端&移动端H5&小程序WebView", doc.text)
        self.assertIn("一、处理", doc.sections)
        self.assertNotIn("replication", doc.text)
        self.assertNotIn("secret", doc.text)

    def test_repository_load_upsert_catalog_and_safe_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            (data_dir / "sop-001.html").write_text(
                "<html><head><title>A</title></head><body><p>正文</p></body></html>",
                encoding="utf-8",
            )
            repo = DocumentRepository(data_dir, HtmlDocumentParser())
            repo.load()
            self.assertEqual("A", repo.get("sop-001").title)
            self.assertTrue((data_dir / "catalog.json").exists())
            doc = repo.upsert_html("sop_002", "<html><title>B</title><body>B正文</body></html>")
            self.assertEqual("sop_002.html", doc.filename)
            self.assertIsNotNone(repo.by_filename("sop_002.html"))
            with self.assertRaises(ValueError):
                repo.upsert_html("../bad", "<html></html>")

    def test_read_file_tool_restricts_to_plain_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            (data_dir / "catalog.json").write_text("[]", encoding="utf-8")
            tool = ReadFileTool(data_dir)
            self.assertEqual("[]", tool.run(fname="catalog.json"))
            with self.assertRaises(ValueError):
                tool.run(fname="../catalog.json")
            with self.assertRaises(ValueError):
                tool.run(fname="*.html")
            with self.assertRaises(FileNotFoundError):
                tool.run(fname="missing.html")

    def test_tool_registry_names_and_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            registry = ToolRegistry([ReadFileTool(Path(tmp))])
            self.assertEqual(["readFile"], registry.names())
            with self.assertRaises(KeyError):
                registry.get("listFiles")

