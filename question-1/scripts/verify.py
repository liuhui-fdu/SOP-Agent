import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import load_config
from app.core.container import AppContainer
from app.reports.markdown import render_markdown
from app.reports.models import CheckResult, VerificationReport
from app.reports.text import render_text


def includes(results, *doc_ids: str) -> bool:
    ids = [item["id"] for item in results]
    return all(doc_id in ids for doc_id in doc_ids)


def first_in(results, *doc_ids: str) -> bool:
    ids = [item["id"] for item in results[: len(doc_ids)]]
    return all(doc_id in ids for doc_id in doc_ids)


def run_checks() -> VerificationReport:
    container = AppContainer(load_config())
    checks = []

    v1_cases = [
        ("v1 OOM", "OOM", lambda r: includes(r, "sop-001")),
        ("v1 故障", "故障", lambda r: len(r) >= 5),
        ("v1 script excluded", "replication", lambda r: len(r) == 0),
        ("v1 CDN", "CDN", lambda r: includes(r, "sop-003", "sop-010")),
        ("v1 ampersand", "&", lambda r: len(r) >= 2),
    ]
    for name, query, predicate in v1_cases:
        results = [item.to_dict() for item in container.keyword_search.search(query)]
        checks.append(CheckResult(name, predicate(results), str([item["id"] for item in results[:5]])))

    v2_cases = [
        ("v2 服务器挂了", "服务器挂了", lambda r: first_in(r, "sop-001", "sop-004")),
        ("v2 黑客攻击", "黑客攻击", lambda r: r and r[0]["id"] == "sop-005"),
        ("v2 机器学习模型", "机器学习模型出问题", lambda r: r and r[0]["id"] == "sop-008"),
    ]
    for name, query, predicate in v2_cases:
        results = [item.to_dict() for item in container.semantic_search.search(query)]
        checks.append(CheckResult(name, predicate(results), str([item["id"] for item in results[:5]])))

    agent_cases = [
        ("agent database", "数据库主从延迟超过30秒怎么处理？", "sop-002.html"),
        ("agent oom", "服务 OOM 了怎么办？", "sop-001.html"),
        ("agent p0", "P0 故障的响应流程是什么？", "sop-001.html"),
        ("agent security", "怀疑有人入侵了系统", "sop-005.html"),
        ("agent recommendation", "推荐结果质量下降了", "sop-008.html"),
    ]
    for name, question, expected_source in agent_cases:
        response = container.agent.chat(question)
        passed = expected_source in response.sources and bool(response.tool_calls)
        detail = f"sources={response.sources}, tools={[call.arguments for call in response.tool_calls]}"
        checks.append(CheckResult(name, passed, detail))

    return VerificationReport("On-Call Assistant Verification Report", checks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="reports")
    args = parser.parse_args()

    report = run_checks()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "verification.md").write_text(render_markdown(report), encoding="utf-8")
    (out_dir / "verification.txt").write_text(render_text(report), encoding="utf-8")
    print(render_text(report))
    raise SystemExit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
