import ast
import sys
import trace
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = ROOT_DIR / "app"
TEST_DIR = ROOT_DIR / "test2"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def executable_lines(path: Path) -> set[int]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    lines: set[int] = set()
    for node in ast.walk(tree):
        lineno = getattr(node, "lineno", None)
        if isinstance(lineno, int):
            lines.add(lineno)
    return lines


def app_files() -> list[Path]:
    return [
        path
        for path in APP_DIR.rglob("*.py")
        if path.name != "__init__.py" and "openai_provider.py" not in str(path) and "codefuse_provider.py" not in str(path)
    ]


def _discover_and_run_tests() -> unittest.result.TestResult:
    suite = unittest.defaultTestLoader.discover(str(TEST_DIR))
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


def run_tests_under_trace() -> tuple[bool, float, int, int]:
    tracer = trace.Trace(count=True, trace=False, ignoredirs=[sys.prefix, sys.exec_prefix])
    result = tracer.runfunc(_discover_and_run_tests)
    counts = tracer.results().counts

    total = 0
    covered = 0
    for path in app_files():
        executable = executable_lines(path)
        if not executable:
            continue
        total += len(executable)
        filename = str(path)
        covered += sum(1 for line in executable if counts.get((filename, line), 0) > 0)
    percent = (covered / total * 100) if total else 100.0
    return result.wasSuccessful(), percent, covered, total


def main() -> None:
    passed, percent, covered, total = run_tests_under_trace()
    print(f"test2 app coverage: {percent:.2f}% ({covered}/{total} executable lines)")
    if not passed:
        raise SystemExit(1)
    if percent < 80.0:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
