import unittest

from app.core.config import load_config
from app.core.container import AppContainer


class V2SemanticTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.container = AppContainer(load_config())

    def ids(self, query: str):
        return [result.id for result in self.container.semantic_search.search(query)]

    def test_server_down(self) -> None:
        self.assertEqual({"sop-001", "sop-004"}, set(self.ids("服务器挂了")[:2]))

    def test_security(self) -> None:
        self.assertEqual("sop-005", self.ids("黑客攻击")[0])

    def test_ai_model(self) -> None:
        self.assertEqual("sop-008", self.ids("机器学习模型出问题")[0])


if __name__ == "__main__":
    unittest.main()
