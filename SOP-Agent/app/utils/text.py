import re
from typing import Iterable, List, Sequence


_SPACE_RE = re.compile(r"\s+")
_ASCII_WORD_RE = re.compile(r"[A-Za-z0-9_+#./-]+")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def normalize_text(value: str) -> str:
    return _SPACE_RE.sub(" ", value or "").strip()


def lower_text(value: str) -> str:
    return normalize_text(value).lower()


def contains_cjk(value: str) -> bool:
    return bool(_CJK_RE.search(value or ""))


def char_ngrams(value: str, min_n: int = 1, max_n: int = 3) -> List[str]:
    compact = re.sub(r"\s+", "", value or "").lower()
    grams: List[str] = []
    for n in range(min_n, max_n + 1):
        if len(compact) >= n:
            grams.extend(compact[i : i + n] for i in range(len(compact) - n + 1))
    return grams


def tokenize(value: str) -> List[str]:
    text = lower_text(value)
    tokens = _ASCII_WORD_RE.findall(text)
    if contains_cjk(text):
        tokens.extend(char_ngrams(text, 2, 3))
    if "&" in text:
        tokens.append("&")
    return [token for token in tokens if token]


def unique_preserve_order(values: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def join_preview(lines: Sequence[str], limit: int = 220) -> str:
    text = normalize_text(" ".join(line for line in lines if line))
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."

