import math
from collections import Counter
from typing import Iterable, Set


def cosine_from_counters(left: Counter, right: Counter) -> float:
    if not left or not right:
        return 0.0
    shared = set(left) & set(right)
    numerator = sum(left[token] * right[token] for token in shared)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


def coverage_score(query_terms: Iterable[str], text_terms: Set[str]) -> float:
    terms = [term for term in query_terms if term]
    if not terms:
        return 0.0
    return sum(1 for term in terms if term in text_terms) / len(terms)

