import unittest

from app.api.pages import chat_page, search_page


class PagesTest(unittest.TestCase):
    def test_search_page_renders(self) -> None:
        html = search_page("Phase 1", "/v1/search")
        self.assertIn("/v1/search", html)
        self.assertIn("escapeHtml", html)

    def test_chat_page_renders(self) -> None:
        html = chat_page()
        self.assertIn("/v3/chat", html)
        self.assertIn("tool_calls", html)


if __name__ == "__main__":
    unittest.main()
