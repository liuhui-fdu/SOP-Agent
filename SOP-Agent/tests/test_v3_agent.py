import unittest

from app.core.config import load_config
from app.core.container import AppContainer


class V3AgentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.container = AppContainer(load_config())

    def test_agent_uses_read_file_only(self) -> None:
        response = self.container.agent.chat("服务 OOM 了怎么办？")
        self.assertIn("sop-001.html", response.sources)
        self.assertTrue(response.tool_calls)
        self.assertEqual({"readFile"}, {call.name for call in response.tool_calls})

    def test_database_question(self) -> None:
        response = self.container.agent.chat("数据库主从延迟超过30秒怎么处理？")
        self.assertIn("sop-002.html", response.sources)


if __name__ == "__main__":
    unittest.main()

