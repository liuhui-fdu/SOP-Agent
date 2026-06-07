import unittest

from app.core.config import load_config
from app.core.container import AppContainer


class V1SearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.container = AppContainer(load_config())

    def ids(self, query: str):
        return [result.id for result in self.container.keyword_search.search(query)]

    def test_oom(self) -> None:
        self.assertIn("sop-001", self.ids("OOM"))

    def test_script_is_not_indexed(self) -> None:
        self.assertEqual([], self.ids("replication"))

    def test_cdn(self) -> None:
        ids = self.ids("CDN")
        self.assertIn("sop-003", ids)
        self.assertIn("sop-010", ids)

    def test_ampersand(self) -> None:
        self.assertGreaterEqual(len(self.ids("&")), 2)


if __name__ == "__main__":
    unittest.main()

