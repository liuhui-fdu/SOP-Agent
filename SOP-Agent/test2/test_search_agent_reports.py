import unittest
from collections import Counter

from app.agent.models import AgentResponse, ToolCall
from app.llm.mock import MockLLMClient
from app.reports.markdown import render_markdown
from app.reports.models import CheckResult, VerificationReport
from app.reports.text import render_text
from app.search.hybrid import HybridSearchProvider
from app.search.scoring import cosine_from_counters, coverage_score
from app.utils.text import char_ngrams, join_preview, normalize_text, tokenize, unique_preserve_order
from test2.helpers import make_temp_container


class SearchAgentReportsExtendedTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir, self.container = make_temp_container()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_keyword_semantic_and_hybrid_search(self) -> None:
        self.assertEqual("sop-001", self.container.keyword_search.search("OOM")[0].id)
        self.assertEqual([], self.container.keyword_search.search("replication"))
        self.assertEqual("sop-005", self.container.semantic_search.search("黑客攻击")[0].id)
        hybrid = HybridSearchProvider(self.container.keyword_search, self.container.semantic_search)
        self.assertIn("sop-001", [item.id for item in hybrid.search("服务器挂了")[:2]])

    def test_agent_sources_and_tool_calls_for_each_readme_case(self) -> None:
        cases = [
            ("数据库主从延迟超过30秒怎么处理？", "sop-002.html"),
            ("服务 OOM 了怎么办？", "sop-001.html"),
            ("P0 故障的响应流程是什么？", "sop-001.html"),
            ("怀疑有人入侵了系统", "sop-005.html"),
        ]
        for question, expected_source in cases:
            with self.subTest(question=question):
                response = self.container.agent.chat(question)
                self.assertIn(expected_source, response.sources)
                self.assertEqual("readFile", response.tool_calls[0].name)

    def test_agent_models_and_report_rendering(self) -> None:
        call = ToolCall("readFile", {"fname": "catalog.json"}, "preview")
        response = AgentResponse("answer", [call], ["catalog.json"])
        self.assertEqual("readFile", response.to_dict()["tool_calls"][0]["name"])
        report = VerificationReport("T", [CheckResult("ok", True, "done")])
        self.assertIn("Overall: PASS", render_text(report))
        self.assertIn("| ok | PASS | done |", render_markdown(report))

    def test_utils_and_scoring_helpers(self) -> None:
        self.assertEqual("a b", normalize_text(" a\n b "))
        self.assertIn("服务", char_ngrams("服务OOM", 2, 2))
        self.assertIn("&", tokenize("网络&CDN"))
        self.assertEqual(["a", "b"], unique_preserve_order(["a", "a", "b"]))
        self.assertTrue(join_preview(["x" * 300], 20).endswith("..."))
        self.assertGreater(cosine_from_counters(Counter(["a", "b"]), Counter(["a"])), 0)
        self.assertEqual(0.5, coverage_score(["a", "b"], {"a"}))

    def test_mock_llm_echoes_latest_message(self) -> None:
        self.assertEqual("hello", MockLLMClient().complete("", [{"role": "user", "content": "hello"}]))
        self.assertEqual("", MockLLMClient().complete("", []))

