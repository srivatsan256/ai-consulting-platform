"""Level verification engine with layered exact, fuzzy, and semantic matching."""
from __future__ import annotations

from difflib import SequenceMatcher
import re
from typing import Any, Dict, List, Tuple

from .level_data import LEVEL_REQUIREMENTS, TOTAL_LEVELS, LEVEL_LABELS

_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}

_SEMANTIC_SYNONYMS = {
    "objective": {"goal", "purpose", "aim", "outcome"},
    "objectives": {"goal", "purpose", "aim", "outcome"},
    "stakeholders": {"users", "users", "clients", "sponsors", "owners", "approvers"},
    "scope": {"boundary", "boundaries", "included", "excluded", "in", "out"},
    "success": {"metric", "metrics", "kpi", "target", "measure", "measurable"},
    "assumptions": {"assumption", "dependency", "dependencies", "constraint", "constraints", "risk"},
    "requirements": {"need", "needs", "specification", "specifications", "expectation", "expectations"},
    "use": {"scenario", "workflow", "process"},
    "case": {"scenario", "workflow", "process"},
    "traceability": {"trace", "mapping", "matrix", "link"},
    "validation": {"acceptance", "criteria", "testable", "verify", "verification"},
    "lifecycle": {"workflow", "process", "handoff", "state"},
    "approvals": {"approval", "signoff", "sign-off", "review"},
    "risks": {"risk", "issue", "blocker", "dependency"},
    "architecture": {"design", "solution", "system", "component"},
    "diagram": {"flow", "mapping", "visual"},
    "integration": {"interface", "contract", "connection", "api"},
    "stack": {"technology", "tools", "backend", "frontend", "database"},
    "frontend": {"ui", "screen", "screens", "layout"},
    "backend": {"api", "service", "services", "logic"},
    "testing": {"test", "tests", "qa", "quality"},
    "security": {"privacy", "access", "control", "vulnerability"},
    "deployment": {"release", "production", "staging", "go-live"},
    "training": {"enablement", "workshop", "onboarding"},
    "governance": {"oversight", "decision", "ownership"},
    "compliance": {"audit", "regulatory", "policy"},
    "acceptance": {"approved", "approval", "signed", "signoff"},
    "closure": {"complete", "completion", "closeout", "final"},
    "handover": {"transition", "handoff", "transfer"},
}


def _tokenize(text: str) -> List[str]:
    return [token for token in _normalize(text).split() if token and token not in _STOPWORDS]


def _normalize(text: str) -> str:
    text = (text or "").lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _expand_tokens(tokens: List[str]) -> List[str]:
    expanded: List[str] = []
    for token in tokens:
        expanded.append(token)
        expanded.extend(sorted(_SEMANTIC_SYNONYMS.get(token, set())))
    return list(dict.fromkeys(expanded))


def _page_records(document_data: Dict[str, Any] | None, document_text: str) -> List[Dict[str, Any]]:
    if document_data and document_data.get("pages"):
        records: List[Dict[str, Any]] = []
        for page in document_data.get("pages", []):
            records.append(
                {
                    "page_number": page.get("page_number"),
                    "text": page.get("text", "") or "",
                    "words": page.get("words", []) or [],
                    "ocr_used": bool(page.get("ocr_used", False)),
                }
            )
        return records

    return [
        {
            "page_number": 1,
            "text": document_text or "",
            "words": [],
            "ocr_used": False,
        }
    ]


def _union_bbox(bboxes: List[List[float]]) -> List[float] | None:
    valid = [bbox for bbox in bboxes if isinstance(bbox, list) and len(bbox) == 4]
    if not valid:
        return None
    return [
        min(bbox[0] for bbox in valid),
        min(bbox[1] for bbox in valid),
        max(bbox[2] for bbox in valid),
        max(bbox[3] for bbox in valid),
    ]


def _word_tokens(words: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    tokens: List[Dict[str, Any]] = []
    for word in words:
        text = _normalize(str(word.get("text", "")))
        if text:
            tokens.append({"text": text, "bbox": word.get("bbox")})
    return tokens


def _phrase_present(text: str, alias: str) -> bool:
    alias_norm = _normalize(alias)
    if not alias_norm:
        return False
    pattern = r"(?<!\w)" + re.escape(alias_norm) + r"(?!\w)"
    return re.search(pattern, text) is not None


def _best_contiguous_match(page_tokens: List[Dict[str, Any]], alias_tokens: List[str]) -> Tuple[float, int | None, int | None]:
    if not page_tokens or not alias_tokens:
        return 0.0, None, None

    token_texts = [token["text"] for token in page_tokens]
    alias_len = len(alias_tokens)
    best_score = 0.0
    best_start: int | None = None
    best_end: int | None = None

    for window_len in {max(1, alias_len - 1), alias_len, alias_len + 1}:
        if window_len > len(token_texts):
            continue
        for start in range(0, len(token_texts) - window_len + 1):
            window = token_texts[start : start + window_len]
            score = SequenceMatcher(None, " ".join(alias_tokens), " ".join(window)).ratio()
            if score > best_score:
                best_score = score
                best_start = start
                best_end = start + window_len - 1

    return best_score, best_start, best_end


def _collect_match_result(
    *,
    page_number: int,
    alias: str,
    match_method: str,
    confidence: float,
    evidence: str,
    coordinates: List[float] | None,
    ocr_used: bool,
) -> Dict[str, Any]:
    return {
        "page_number": page_number,
        "matched_term": alias,
        "match_method": match_method,
        "confidence": round(max(0.0, min(confidence, 0.99)), 2),
        "evidence": evidence,
        "coordinates": coordinates,
        "ocr_used": ocr_used,
    }


def _best_match_for_alias(page: Dict[str, Any], alias: str) -> Dict[str, Any] | None:
    page_text = page.get("text", "") or ""
    normalized_text = _normalize(page_text)
    alias_norm = _normalize(alias)
    if not alias_norm:
        return None

    if _phrase_present(normalized_text, alias):
        token_list = _word_tokens(page.get("words", []))
        alias_tokens = _tokenize(alias)
        coordinates = None
        if token_list:
            best_score, start, end = _best_contiguous_match(token_list, alias_tokens)
            if start is not None and end is not None and best_score >= 0.85:
                coordinates = _union_bbox([token_list[idx]["bbox"] for idx in range(start, end + 1) if token_list[idx].get("bbox")])
        snippet_index = normalized_text.find(alias_norm)
        snippet = page_text[max(0, snippet_index - 80) : min(len(page_text), snippet_index + len(alias) + 80)] if snippet_index >= 0 else page_text[:180]
        return _collect_match_result(
            page_number=int(page.get("page_number") or 1),
            alias=alias,
            match_method="exact",
            confidence=0.99,
            evidence=snippet.strip(),
            coordinates=coordinates,
            ocr_used=bool(page.get("ocr_used", False)),
        )

    token_list = _word_tokens(page.get("words", []))
    alias_tokens = _tokenize(alias)
    if token_list and alias_tokens:
        fuzzy_score, start, end = _best_contiguous_match(token_list, alias_tokens)
        if fuzzy_score >= 0.78 and start is not None and end is not None:
            coordinates = _union_bbox([token_list[idx]["bbox"] for idx in range(start, end + 1) if token_list[idx].get("bbox")])
            evidence = " ".join(token_list[idx]["text"] for idx in range(start, end + 1))
            return _collect_match_result(
                page_number=int(page.get("page_number") or 1),
                alias=alias,
                match_method="fuzzy",
                confidence=0.72 + (fuzzy_score * 0.2),
                evidence=evidence,
                coordinates=coordinates,
                ocr_used=bool(page.get("ocr_used", False)),
            )

    semantic_tokens = set(_expand_tokens(_tokenize(alias)))
    page_tokens = set(_tokenize(page_text))
    overlap = semantic_tokens & page_tokens
    if overlap:
        score = len(overlap) / max(len(semantic_tokens), 1)
        if score >= 0.18:
            matched_words = [word for word in page.get("words", []) if _normalize(str(word.get("text", ""))) in overlap]
            coordinates = _union_bbox([word.get("bbox") for word in matched_words if word.get("bbox")])
            evidence = page_text[:220]
            return _collect_match_result(
                page_number=int(page.get("page_number") or 1),
                alias=alias,
                match_method="semantic",
                confidence=0.58 + (score * 0.32),
                evidence=evidence.strip(),
                coordinates=coordinates,
                ocr_used=bool(page.get("ocr_used", False)),
            )

    return None


def _match_requirement(text: str, aliases: List[str], document_data: Dict[str, Any] | None = None) -> Tuple[bool, Dict[str, Any]]:
    pages = _page_records(document_data, text)
    best_result: Dict[str, Any] | None = None

    for page in pages:
        for alias in aliases:
            result = _best_match_for_alias(page, alias)
            if not result:
                continue
            if not best_result or result["confidence"] > best_result["confidence"]:
                best_result = result

    if best_result:
        return True, best_result
    return False, {
        "page_number": None,
        "matched_term": None,
        "match_method": None,
        "confidence": 0.0,
        "evidence": "",
        "coordinates": None,
        "ocr_used": False,
    }


def verify_level_document(document_text: str, level: int, document_data: Dict[str, Any] | None = None) -> Dict[str, Any]:
    level = max(1, min(int(level or 1), TOTAL_LEVELS))
    config = LEVEL_REQUIREMENTS[level]
    requirements: List[Dict[str, Any]] = []
    required_docs = config.get("required_documents", [])

    for requirement in config["requirements"]:
        matched, evidence = _match_requirement(document_text, requirement["aliases"], document_data=document_data)
        requirements.append(
            {
                "key": requirement["key"],
                "label": requirement["label"],
                "status": "matched" if matched else "not_matched",
                "matched": matched,
                "evidence": evidence["evidence"],
                "page_number": evidence["page_number"],
                "coordinates": evidence["coordinates"],
                "confidence": evidence["confidence"],
                "match_method": evidence["match_method"],
                "matched_term": evidence["matched_term"],
                "ocr_used": evidence["ocr_used"],
                "aliases": requirement["aliases"],
            }
        )

    matched_count = sum(1 for item in requirements if item["matched"])
    total = len(requirements) or 1
    passed = matched_count == total

    return {
        "level": level,
        "level_label": LEVEL_LABELS.get(level, str(level)),
        "level_title": config["title"],
        "level_icon": config.get("icon", "folder"),
        "level_color": config.get("color", "gray"),
        "required_documents": [
            {"doc_type": doc["doc_type"], "label": doc["label"], "keywords": doc["keywords"]}
            for doc in required_docs
        ],
        "level_status": "PASSED" if passed else "FAILED",
        "unlock_next_level": passed,
        "score": round((matched_count / total) * 100, 2),
        "passed": passed,
        "status": passed,
        "requirements": requirements,
        "missing_requirements": [item["label"] for item in requirements if not item["matched"]],
    }


def verify_documents_for_level(documents: List[Dict[str, Any]], level: int) -> Dict[str, Any]:
    combined_text = "\n".join((doc.get("extracted_text") or doc.get("text") or "") for doc in documents)
    combined_pages: List[Dict[str, Any]] = []
    for doc in documents:
        extraction = doc.get("extraction") or doc.get("structured_extraction") or {}
        combined_pages.extend(extraction.get("pages", []) or [])
    structured = {"pages": combined_pages} if combined_pages else None
    return verify_level_document(combined_text, level, document_data=structured)
