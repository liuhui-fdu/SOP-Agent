import json
import re
from typing import Iterable, List, Tuple

from app.agent.models import AgentResponse, ToolCall
from app.documents.parsers.html_parser import HtmlDocumentParser
from app.tools.registry import ToolRegistry
from app.utils.text import join_preview, normalize_text


class OnCallAgentService:
    def __init__(self, tools: ToolRegistry, max_steps: int = 6) -> None:
        if tools.names() != ["readFile"]:
            raise ValueError("Phase 3 agent must expose only readFile")
        self.tools = tools
        self.max_steps = max_steps
        self.html_parser = HtmlDocumentParser()

    def chat(self, question: str) -> AgentResponse:
        tool_calls: List[ToolCall] = []
        catalog_text = self._read_file("catalog.json", tool_calls)
        catalog = json.loads(catalog_text)
        selected_files = self._select_files(question, catalog)
        selected_files = selected_files[: max(1, self.max_steps - 1)]

        documents = []
        for filename in selected_files:
            html = self._read_file(filename, tool_calls)
            doc_id = filename.rsplit(".", 1)[0]
            documents.append(self.html_parser.parse(doc_id, filename, html))

        answer = self._compose_answer(question, documents)
        return AgentResponse(
            answer=answer,
            tool_calls=tool_calls,
            sources=[document.filename for document in documents],
        )

    def _read_file(self, filename: str, tool_calls: List[ToolCall]) -> str:
        content = self.tools.get("readFile").run(fname=filename)
        tool_calls.append(
            ToolCall(
                name="readFile",
                arguments={"fname": filename},
                result_preview=join_preview([content], limit=180),
            )
        )
        return content

    def _select_files(self, question: str, catalog: List[dict]) -> List[str]:
        query = normalize_text(question)
        explicit = self._explicit_file_matches(query)
        if explicit:
            return self._catalog_order(explicit, catalog)

        scored: List[Tuple[float, str]] = []
        for item in catalog:
            filename = item.get("filename", "")
            text = normalize_text(
                " ".join(
                    [
                        item.get("title", ""),
                        " ".join(item.get("sections", [])),
                        item.get("preview", ""),
                    ]
                )
            )
            score = self._semantic_score(query, text)
            if score > 0:
                scored.append((score, filename))
        scored.sort(key=lambda pair: (-pair[0], pair[1]))
        if scored:
            return [filename for _, filename in scored[:3]]
        return [item["filename"] for item in catalog[:1]]

    def _explicit_file_matches(self, question: str) -> List[str]:
        rules = [
            (["数据库", "主从", "复制", "延迟", "慢查询", "连接池"], ["sop-002.html"]),
            (["oom", "内存", "OutOfMemoryError", "服务"], ["sop-001.html"]),
            (["黑客", "入侵", "安全", "漏洞", "攻击"], ["sop-005.html"]),
            (["推荐", "模型", "机器学习", "算法", "GPU", "质量下降"], ["sop-008.html"]),
            (["白屏", "前端", "页面", "JS错误"], ["sop-003.html"]),
            (["CDN", "DNS", "网络", "DDoS"], ["sop-010.html"]),
            (["P0", "故障", "响应流程", "升级"], ["sop-001.html", "sop-004.html", "sop-005.html", "sop-010.html"]),
        ]
        lowered = question.lower()
        matched: List[str] = []
        for terms, filenames in rules:
            if any(term.lower() in lowered for term in terms):
                matched.extend(filenames)
        return list(dict.fromkeys(matched))

    def _catalog_order(self, filenames: Iterable[str], catalog: List[dict]) -> List[str]:
        available = {item.get("filename") for item in catalog}
        return [filename for filename in filenames if filename in available]

    def _semantic_score(self, query: str, text: str) -> float:
        score = 0.0
        for token in self._tokens(query):
            if token and token in text:
                score += 1.0
        return score

    def _tokens(self, text: str) -> List[str]:
        ascii_terms = re.findall(r"[A-Za-z0-9_+#-]+", text)
        cjk_terms = re.findall(r"[\u4e00-\u9fff]{2,}", text)
        grams = []
        for term in cjk_terms:
            grams.extend(term[i : i + 2] for i in range(max(0, len(term) - 1)))
        return ascii_terms + cjk_terms + grams

    def _compose_answer(self, question: str, documents) -> str:
        if not documents:
            return "未找到相关 SOP，请补充故障现象或系统范围。"

        question_lower = question.lower()
        lines = [
            "根据已读取的 SOP，建议按下面步骤处理：",
            "",
        ]
        for document in documents:
            relevant = self._relevant_paragraphs(question, document.text)
            lines.append(f"来源：{document.title}（{document.filename}）")
            if relevant:
                for index, paragraph in enumerate(relevant[:4], start=1):
                    lines.append(f"{index}. {paragraph}")
            else:
                lines.append(f"1. {document.text[:260]}")
            lines.append("")

        if "p0" in question_lower or "故障" in question:
            lines.extend(
                [
                    "通用升级要求：先确认影响范围和业务链路，五分钟内升级到负责人；同步已采取措施、当前判断和下一步计划；必要时拉起统一沟通频道或 War Room；处理后补齐值班日志和复盘记录。",
                    "",
                ]
            )
        lines.append("注意：高风险操作如生产变更、数据删除、主从切换、DNS/CDN 全量刷新，应先完成确认和审批。")
        return "\n".join(lines).strip()

    def _relevant_paragraphs(self, question: str, text: str) -> List[str]:
        paragraphs = [normalize_text(item) for item in re.split(r"(?<=[。！？])\s*", text) if normalize_text(item)]
        tokens = set(self._tokens(question))
        scored: List[Tuple[float, str]] = []
        for paragraph in paragraphs:
            score = sum(1 for token in tokens if token and token in paragraph)
            if "升级" in paragraph or "P0" in paragraph:
                score += 0.5
            if score > 0:
                scored.append((score, paragraph))
        scored.sort(key=lambda pair: -pair[0])
        return [paragraph for _, paragraph in scored[:6]]

