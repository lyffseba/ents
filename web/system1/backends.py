"""System 1 backends: local Laya, Jev-on-OpenRouter, and a heuristic mock.

The mock is the CI and demo path. Laya (`web.system1.laya`, the published
``Router.predict`` API) and Jev are used when selected and reachable. A
missing Laya install or weight download is remembered for the process so
later requests do not retry a multi-hundred-megabyte fetch. A predict error
after the router has loaded falls back for that call only. Jev HTTP failures
fall back per call.
"""

from __future__ import annotations

import math
import re
from typing import Any

from ..config import (
    openrouter_api_key,
    openrouter_decisions_url,
    system1_backend_setting,
    system1_jev_model,
)

_WORD = re.compile(r"[a-z0-9]{4,}")

_router: Any = None
_laya_block_reason: str | None = None


class BackendUnavailable(Exception):
    """Selected backend cannot answer; the bus should use the mock."""


def reset_backend_state() -> None:
    """Clear cached Laya client / failure. Used by tests."""
    global _router, _laya_block_reason
    _router = None
    _laya_block_reason = None


def requested_backend() -> str:
    """Explicit setting, or ``laya`` when unset (preferred local default)."""
    setting = system1_backend_setting()
    if setting in {"laya", "openrouter_jev", "mock"}:
        return setting
    if setting:
        return "mock"
    return "laya"


def predict(state: Any, questions: dict) -> dict:
    """Score ``questions`` over ``state``. Always returns mock-or-better answers."""
    requested = requested_backend()
    if requested == "mock":
        return _pack("mock", requested, mock_answers(state, questions), None, None)

    try:
        if requested == "laya":
            answers, model = laya_answers(state, questions)
            return _pack("laya", requested, answers, None, model)
        if requested == "openrouter_jev":
            answers, model = jev_answers(state, questions)
            return _pack("openrouter_jev", requested, answers, None, model)
    except BackendUnavailable as exc:
        return _pack("mock", requested, mock_answers(state, questions), str(exc), None)

    return _pack("mock", requested, mock_answers(state, questions), f"unknown backend {requested}", None)


def laya_importable() -> bool:
    try:
        import laya  # noqa: F401
    except ImportError:
        return False
    return True


def laya_answers(state: Any, questions: dict) -> tuple[dict, str | None]:
    """One Laya forward pass. Raises ``BackendUnavailable`` if weights are missing.

    The router is built by ``web.system1.laya.open_router`` (published
    ``laya.Router``). A failed import or checkpoint load is remembered for
    the process. A later ``predict`` error is not: the loaded router stays.
    """
    global _router, _laya_block_reason
    if _laya_block_reason:
        raise BackendUnavailable(_laya_block_reason)
    from . import laya as laya_runtime

    try:
        if _router is None:
            _router = laya_runtime.open_router()
    except ImportError as exc:
        _laya_block_reason = f"laya package not installed ({exc})"
        raise BackendUnavailable(_laya_block_reason) from exc
    except laya_runtime.LayaNotReady as exc:
        if exc.sticky:
            _laya_block_reason = str(exc)
            _router = None
        raise BackendUnavailable(str(exc)) from exc
    except Exception as exc:
        _laya_block_reason = f"laya weights unavailable ({type(exc).__name__}: {exc})"
        _router = None
        raise BackendUnavailable(_laya_block_reason) from exc

    try:
        result = laya_runtime.run_predict(_router, state, questions)
    except laya_runtime.LayaNotReady as exc:
        if exc.sticky:
            _laya_block_reason = str(exc)
        raise BackendUnavailable(str(exc)) from exc
    except Exception as exc:
        raise BackendUnavailable(f"laya predict failed ({type(exc).__name__}: {exc})") from exc

    if not isinstance(result, dict) or not isinstance(result.get("answers"), dict):
        raise BackendUnavailable("laya predict() did not return an answers object")
    return _normalize_answers(result["answers"], questions), _laya_served_model(result)


def _laya_served_model(result: dict) -> str | None:
    """Hub id when Laya reports one, otherwise the checkpoint name."""
    routing = result.get("routing") if isinstance(result.get("routing"), dict) else {}
    repo = routing.get("repo")
    name = routing.get("model")
    if isinstance(repo, str) and repo.strip():
        return repo.strip()
    if isinstance(name, str) and name.strip():
        return name.strip()
    return None


def jev_answers(state: Any, questions: dict) -> tuple[dict, str | None]:
    """TypeSafe Jev via the OpenRouter Decisions API."""
    key = openrouter_api_key()
    if not key:
        raise BackendUnavailable("OPENROUTER_API_KEY unset")
    import httpx

    model = system1_jev_model()
    try:
        response = httpx.post(
            openrouter_decisions_url(),
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/lyffseba/ents",
                "X-OpenRouter-Title": "Ents Academy",
            },
            json={"model": model, "state": state, "questions": questions},
            timeout=30.0,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        raise BackendUnavailable(f"openrouter jev request failed ({type(exc).__name__}: {exc})") from exc

    answers = _extract_answers(payload)
    if not isinstance(answers, dict) or not answers:
        raise BackendUnavailable("openrouter jev response missing answers")
    served = payload.get("model") if isinstance(payload, dict) else None
    return _normalize_answers(answers, questions), (str(served) if served else model)


def mock_answers(state: Any, questions: dict) -> dict:
    """Deterministic lexical heuristic. Distinctive shared words raise confidence."""
    text = state_text(state)
    answers: dict = {}
    for name, question in questions.items():
        qtype = question.get("type")
        if qtype == "choice":
            answers[name] = _mock_choice(text, question.get("criteria"))
        elif qtype == "score":
            answers[name] = _mock_score(text, question.get("criteria") or [])
        elif qtype == "noul":
            answers[name] = _mock_noul(text, str(question.get("instructions") or ""))
        else:
            answers[name] = {"confidence": 0.0}
    return answers


def state_text(state: Any) -> str:
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        parts = []
        for key in ("text", "question", "body", "message", "subject"):
            value = state.get(key)
            if isinstance(value, str) and value.strip():
                parts.append(value.strip())
        if parts:
            return "\n".join(parts)
        import json
        return json.dumps(state, ensure_ascii=False, default=str)
    return str(state)


def _pack(backend: str, requested: str, answers: dict, fallback: str | None, model: str | None) -> dict:
    return {
        "answers": answers,
        "backend": backend,
        "requested_backend": requested,
        "fallback_reason": fallback,
        "model": model,
    }


def _extract_answers(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return None
    if isinstance(payload.get("answers"), dict):
        return payload["answers"]
    for key in ("result", "decision", "output"):
        nested = payload.get(key)
        if isinstance(nested, dict) and isinstance(nested.get("answers"), dict):
            return nested["answers"]
    return None


def _normalize_answers(raw: dict, questions: dict) -> dict:
    from .gate import answer_confidence

    normalized: dict = {}
    for name, question in questions.items():
        answer = raw.get(name)
        qtype = question.get("type")
        if isinstance(answer, (int, float)) and not isinstance(answer, bool) and qtype == "noul":
            answer = {"noul": float(answer)}
        if not isinstance(answer, dict):
            answer = {}
        item = _json_ready(answer)
        if qtype == "choice" and "choice" not in item and isinstance(item.get("probabilities"), dict):
            probs = item["probabilities"]
            if probs:
                item["choice"] = max(probs, key=lambda k: _as_float(probs[k]))
        if qtype == "noul" and "noul" not in item and "probability" in item:
            item["noul"] = _as_float(item["probability"])
        if "confidence" not in item or item.get("confidence") is None:
            item["confidence"] = round(answer_confidence(item), 4)
        else:
            item["confidence"] = round(_as_float(item["confidence"]), 4)
        normalized[name] = item
    return normalized


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(v) for v in value]
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        return float(value)
    if hasattr(value, "item") and callable(value.item):
        try:
            return _json_ready(value.item())
        except Exception:
            return str(value)
    return str(value)


def _words(text: str) -> set[str]:
    return set(_WORD.findall(text.lower()))


def _overlap(left: set[str], right: set[str]) -> int:
    if not left or not right:
        return 0
    count = len(left & right)
    for word in left - right:
        if len(word) < 5:
            continue
        for other in right:
            if len(other) >= 5 and (word.startswith(other) or other.startswith(word)):
                count += 1
                break
    return count


def _softmax(scores: list[float]) -> list[float]:
    if not scores:
        return []
    peak = max(scores)
    exps = [math.exp(score - peak) for score in scores]
    total = sum(exps) or 1.0
    return [value / total for value in exps]


def _margin_confidence(probs: list[float]) -> float:
    ordered = sorted(probs, reverse=True)
    if not ordered:
        return 0.0
    top = ordered[0]
    second = ordered[1] if len(ordered) > 1 else 0.0
    return round(min(0.99, 0.50 + (top - second)), 4)


def _mock_choice(text: str, criteria: Any) -> dict:
    items = _choice_items(criteria)
    if not items:
        return {"choice": "", "probabilities": {}, "confidence": 0.0}
    state_words = _words(text)
    option_words = [_words(f"{key} {desc}") for key, desc in items]
    raw: list[float] = []
    for index, words in enumerate(option_words):
        score = float(_overlap(state_words, words))
        others: set[str] = set()
        for j, extra in enumerate(option_words):
            if j != index:
                others |= extra
        unique = {w for w in (words & state_words) if len(w) >= 6 and w not in others}
        score += 2.0 * len(unique)
        raw.append(score)
    labels = [key for key, _desc in items]
    if sum(raw) <= 0:
        uniform = 1.0 / len(labels)
        probs = {label: round(uniform, 4) for label in labels}
        return {"choice": labels[0], "probabilities": probs, "confidence": round(uniform, 4)}
    dist = _softmax(raw)
    best = max(range(len(labels)), key=lambda i: dist[i])
    return {
        "choice": labels[best],
        "probabilities": {label: round(dist[i], 4) for i, label in enumerate(labels)},
        "confidence": _margin_confidence(dist),
    }


def _choice_items(criteria: Any) -> list[tuple[str, str]]:
    if isinstance(criteria, dict):
        return [(str(key), str(desc)) for key, desc in criteria.items()]
    if isinstance(criteria, list):
        return [(str(item), str(item)) for item in criteria]
    return []


def _mock_score(text: str, criteria: list) -> dict:
    labels = [str(item) for item in criteria] or ["low", "high"]
    picked = _mock_choice(text, {label: label for label in labels})
    probs_map = picked["probabilities"]
    dist = [float(probs_map.get(label, 0.0)) for label in labels]
    if sum(dist) <= 0:
        dist = [1.0 / len(labels)] * len(labels)
    score = sum(index * prob for index, prob in enumerate(dist))
    return {
        "score": round(score, 4),
        "probabilities": [round(p, 4) for p in dist],
        "confidence": picked["confidence"],
    }


def _mock_noul(text: str, instructions: str) -> dict:
    instr = instructions.lower()
    lowered = text.lower()
    if any(token in instr for token in ("generat", "personalized", "fixed template", "glossary")):
        p = _needs_generation_probability(lowered)
    else:
        cues = [word for word in ("cancel", "quit", "refund", "abandon", "churn", "phish", "scam", "urgent", "stuck") if word in instr]
        if not cues:
            p = 0.5 if len(lowered.split()) <= 2 else 0.2
        else:
            hits = sum(1 for word in cues if word in lowered)
            p = 0.08 if hits == 0 else 0.15 + 0.8 * (hits / len(cues))
    p = max(0.0, min(1.0, p))
    return {"noul": round(p, 4), "confidence": round(abs(p - 0.5) * 2, 4)}


def _needs_generation_probability(text: str) -> float:
    """Known Ents templates do not need a drafted paragraph."""
    glossary = ("softmax", "embedding", "bigram", "tokenizer", "attention")
    has_glossary = any(term in text for term in glossary)
    if any(phrase in text for phrase in ("what is", "what's", "define ")) and has_glossary:
        return 0.04
    if "stuck" in text and "days" in text:
        return 0.05
    if any(word in text for word in ("cancel", "refund", "quit", "abandon")):
        return 0.06
    if len(text.split()) <= 2:
        return 0.55
    return 0.86


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
