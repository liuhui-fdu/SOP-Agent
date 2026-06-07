from app.agent.service import OnCallAgentService
from app.core.config import AppConfig
from app.documents.parsers.html_parser import HtmlDocumentParser
from app.documents.repository import DocumentRepository
from app.search.hybrid import HybridSearchProvider
from app.search.keyword import KeywordSearchProvider
from app.search.semantic import SemanticSearchProvider
from app.tools.read_file import ReadFileTool
from app.tools.registry import ToolRegistry


class AppContainer:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.parser = HtmlDocumentParser()
        self.repository = DocumentRepository(config.data_dir, self.parser)
        self.repository.load()
        self._build_search_providers()
        self.tools = ToolRegistry([ReadFileTool(config.data_dir)])
        self.agent = OnCallAgentService(self.tools, max_steps=config.agent.max_steps)

    def _build_search_providers(self) -> None:
        documents = self.repository.all()
        self.keyword_search = KeywordSearchProvider(documents, top_k=self.config.search.top_k)
        self.semantic_search = SemanticSearchProvider(
            documents,
            concepts=self.config.search.semantic_concepts,
            top_k=self.config.search.top_k,
        )
        self.hybrid_search = HybridSearchProvider(
            self.keyword_search,
            self.semantic_search,
            keyword_weight=self.config.search.keyword_weight,
            semantic_weight=self.config.search.semantic_weight,
        )

    def reindex(self) -> None:
        self._build_search_providers()

