import unittest

from app.documents.parsers.html_parser import HtmlDocumentParser


class HtmlParserTest(unittest.TestCase):
    def test_excludes_script_and_decodes_entities(self) -> None:
        html = """
        <html><head><title>A&amp;B</title><script>replication</script></head>
        <body><h1>Title</h1><p>网络&amp;CDN</p><style>.x{}</style></body></html>
        """
        document = HtmlDocumentParser().parse("x", "x.html", html)
        self.assertEqual(document.title, "A&B")
        self.assertIn("网络&CDN", document.text)
        self.assertNotIn("replication", document.text)


if __name__ == "__main__":
    unittest.main()

