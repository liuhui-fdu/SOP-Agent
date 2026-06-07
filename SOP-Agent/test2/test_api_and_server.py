import json
import unittest

from app.api import v1, v2, v3
from app.api.pages import chat_page, search_page
from app.server import extract_q
from test2.helpers import make_temp_container


class ApiAndServerExtendedTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir, self.container = make_temp_container()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_extract_q_handles_encoded_ampersand_and_empty_query(self) -> None:
        self.assertEqual("&", extract_q("q=%26"))
        self.assertEqual("&", extract_q("q=&"))
        self.assertEqual("", extract_q("q="))
        self.assertEqual("", extract_q(""))

    def test_v1_document_post_reindexes_visible_text_only(self) -> None:
        payload = {
            "id": "sop-new",
            "html": "<html><head><title>新增 SOP</title><script>hidden-hit</script></head>"
            "<body><main><p>新增正文 keyword-visible</p></main></body></html>",
        }
        result = v1.create_document(self.container, payload)
        self.assertEqual({"id": "sop-new", "title": "新增 SOP"}, result)
        self.assertIn("sop-new", [item["id"] for item in v1.search(self.container, "keyword-visible")["results"]])
        self.assertEqual([], v1.search(self.container, "hidden-hit")["results"])

    def test_v2_and_v3_api_shapes(self) -> None:
        semantic = v2.search(self.container, "黑客攻击")
        self.assertEqual("sop-005", semantic["results"][0]["id"])
        chat = v3.chat(self.container, {"message": "服务 OOM 了怎么办？"})
        self.assertIn("answer", chat)
        self.assertIn("sop-001.html", chat["sources"])
        self.assertEqual("readFile", chat["tool_calls"][0]["name"])

    def test_pages_render_fetch_targets_and_escape_function(self) -> None:
        self.assertIn("/v1/search", search_page("Phase 1", "/v1/search"))
        page = chat_page()
        self.assertIn("/v3/chat", page)
        self.assertIn("escapeHtml", page)

    def test_json_serializable_api_responses(self) -> None:
        payload = v1.search(self.container, "OOM")
        encoded = json.dumps(payload, ensure_ascii=False)
        self.assertIn("sop-001", encoded)

