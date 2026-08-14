"""
Token reduction utilities for the AI service.

Implements a set of techniques to reduce LLM token usage and cost:

- ``estimate_tokens``      -> cheap token counting (tiktoken when available)
- ``truncate``             -> hard truncation to a token budget
- ``split_text``           -> chunking with token-aware sizes + overlap
- ``distill``              -> extractive distillation (keeps important content)
- ``LlmCache``             -> bounded LRU cache to avoid repeat calls

Everything here is deterministic and dependency-light so it can be used
anywhere in the backend.
"""

from __future__ import annotations

import hashlib
import re
from collections import OrderedDict
from functools import lru_cache
from typing import Optional

_encoder = None
_encoder_checked = False


def _get_encoder():
    """Return a tiktoken encoder, or None if tiktoken is unavailable."""
    global _encoder, _encoder_checked
    if not _encoder_checked:
        _encoder_checked = True
        try:
            import tiktoken  # type: ignore

            _encoder = tiktoken.get_encoding("cl100k_base")
        except Exception:
            _encoder = None
    return _encoder


def estimate_tokens(text: str) -> int:
    """Estimate the number of tokens in ``text``.

    Uses tiktoken when available, otherwise falls back to the standard
    ~4 characters per token heuristic.
    """
    if not text:
        return 0
    encoder = _get_encoder()
    if encoder is not None:
        try:
            return len(encoder.encode(text))
        except Exception:
            pass
    return max(1, int(len(text) / 4))


def truncate(text: str, max_tokens: int) -> str:
    """Truncate ``text`` so it fits within ``max_tokens`` tokens."""
    if max_tokens <= 0:
        return ""
    if not text:
        return text
    if estimate_tokens(text) <= max_tokens:
        return text
    encoder = _get_encoder()
    if encoder is not None:
        try:
            return encoder.decode(encoder.encode(text)[:max_tokens])
        except Exception:
            pass
    return text[: max_tokens * 4]


def _tail(text: str, max_tokens: int) -> str:
    """Return the trailing ``max_tokens`` tokens of ``text``."""
    if max_tokens <= 0:
        return ""
    encoder = _get_encoder()
    if encoder is not None:
        try:
            tokens = encoder.encode(text)
            if len(tokens) <= max_tokens:
                return text
            return encoder.decode(tokens[-max_tokens:])
        except Exception:
            pass
    return text[-max_tokens * 4 :]


def split_text(text: str, chunk_tokens: int = 1024, overlap_tokens: int = 128) -> list:
    """Split ``text`` into overlapping chunks bounded by ``chunk_tokens``.

    Splits on paragraph boundaries first, then falls back to sentences and
    finally raw character slices so no chunk exceeds the token budget.
    """
    if not text:
        return []
    if estimate_tokens(text) <= chunk_tokens:
        return [text]

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    chunks: list = []
    current = ""

    for para in paragraphs:
        while estimate_tokens(para) > chunk_tokens:
            if current:
                chunks.append(current)
            head = truncate(para, chunk_tokens)
            chunks.append(head)
            para = para[len(head) :].strip()
            current = ""
            if not para:
                break
        if not para:
            continue
        combined = f"{current}\n\n{para}".strip() if current else para
        if current and estimate_tokens(combined) > chunk_tokens:
            chunks.append(current)
            current = f"{_tail(current, overlap_tokens)}\n\n{para}".strip()
        else:
            current = combined

    if current:
        chunks.append(current)
    return chunks


_IMPORTANCE_KEYWORDS = re.compile(
    r"(business|objective|goal|problem|risk|cost|roi|timeline|scope|metric|"
    r"user|client|stakeholder|deadline|budget|deliverable|kpi|revenue|"
    r"executive|summary|recommendation|approach|next step)",
    re.IGNORECASE,
)

_HEADING_WORDS = (
    "Executive",
    "Summary",
    "Objective",
    "Goals",
    "Approach",
    "Recommendation",
    "Risk",
    "ROI",
    "Timeline",
    "Deliverable",
    "KPI",
)


def _sentence_score(sentence: str) -> int:
    score = 0
    if re.search(r"\d", sentence):
        score += 2
    if len(sentence) > 80:
        score += 1
    score += len(_IMPORTANCE_KEYWORDS.findall(sentence))
    for word in _HEADING_WORDS:
        if word in sentence:
            score += 3
            break
    return score


def distill(text: str, target_tokens: int) -> str:
    """Extractively distill ``text`` down to ``target_tokens`` tokens.

    Scores each sentence by importance (keywords, numbers, headings) and
    keeps the highest-scoring subset within budget, preserving original
    order. Falls back to ``truncate`` for pathological inputs.
    """
    if not text or target_tokens <= 0:
        return ""
    if estimate_tokens(text) <= target_tokens:
        return text

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if len(sentences) < 2:
        return truncate(text, target_tokens)

    scored = sorted(
        ((_sentence_score(s), s) for s in sentences),
        key=lambda pair: pair[0],
        reverse=True,
    )

    kept: list = []
    used = 0
    for score, sentence in scored:
        token_count = estimate_tokens(sentence)
        if used + token_count <= target_tokens:
            kept.append(sentence)
            used += token_count

    kept_set = set(kept)
    ordered = [s for s in sentences if s in kept_set]
    result = " ".join(ordered)
    if estimate_tokens(result) > target_tokens:
        result = truncate(result, target_tokens)
    return result or truncate(text, target_tokens)


class LlmCache:
    """Bounded in-memory LRU cache for LLM responses.

    Keys are content hashes so large prompt strings are never retained.
    """

    def __init__(self, max_entries: int = 512):
        self._data: "OrderedDict[str, str]" = OrderedDict()
        self._max = max_entries

    def get(self, key: str) -> Optional[str]:
        if key in self._data:
            self._data.move_to_end(key)
            return self._data[key]
        return None

    def set(self, key: str, value: str) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = value
        while len(self._data) > self._max:
            self._data.popitem(last=False)

    def clear(self) -> None:
        self._data.clear()

    @property
    def size(self) -> int:
        return len(self._data)


def make_cache_key(
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    response_format: Optional[dict] = None,
) -> str:
    """Build a stable cache key from the exact generation inputs."""
    raw = "|".join(
        (
            provider or "",
            model or "",
            system_prompt or "",
            user_prompt or "",
            str(temperature),
            str(max_tokens),
            str(response_format),
        )
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@lru_cache(maxsize=1)
def get_cache() -> LlmCache:
    """Shared, process-wide response cache."""
    return LlmCache()
