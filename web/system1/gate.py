"""Pure confidence policy. No network, no database."""

from __future__ import annotations

from ..config import (
    system1_high_confidence,
    system1_needs_generation_threshold,
    system2_cost_tier_override,
)

_COST_TIERS = ("low", "medium", "high", "xhigh", "max")


def answer_confidence(answer: dict) -> float:
    """Confidence in ``[0, 1]``. Noul without a confidence field uses ``|2p-1|``."""
    if not isinstance(answer, dict):
        return 0.0
    if answer.get("confidence") is not None:
        try:
            return max(0.0, min(1.0, float(answer["confidence"])))
        except (TypeError, ValueError):
            return 0.0
    if "noul" in answer:
        try:
            p = float(answer["noul"])
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, abs(p - 0.5) * 2))
    probs = answer.get("probabilities")
    values: list[float] = []
    if isinstance(probs, dict):
        values = [_as_float(v) for v in probs.values()]
    elif isinstance(probs, list):
        values = [_as_float(v) for v in probs]
    if values:
        return max(values)
    return 0.0


def routing_confidence(answers: dict) -> float:
    """Confidence that gates the route.

    Choice answers and the optional ``needs_generation`` noul are the routing
    signals. Other score/noul answers stay on the record for templates and
    drafts, and do not veto a confident choice.
    """
    if not answers:
        return 0.0
    signals: list[float] = []
    for name, answer in answers.items():
        if not isinstance(answer, dict):
            continue
        if "choice" in answer or name == "needs_generation":
            signals.append(answer_confidence(answer))
    if not signals:
        signals = [answer_confidence(a) for a in answers.values() if isinstance(a, dict)]
    return min(signals) if signals else 0.0


def auto_cost_tier(answers: dict | None) -> str:
    """Map System 1 urgency (else difficulty) onto an Auto Router ``cost_tier``.

    No score → ``low`` (the band Auto uses when ``cost_tier`` is omitted).
    ``SYSTEM2_COST_TIER`` wins when it is one of low|medium|high|xhigh|max.

    The score is a weighted index. Divide by the highest probability index
    (or by 2 when the score is above 1 and no support is present). Bands on
    that 0–1 position: <0.20 low, <0.40 medium, <0.60 high, <0.80 xhigh,
    otherwise max. Confidence below 0.5 steps down one band, not below low.
    """
    override = system2_cost_tier_override()
    if override:
        return override
    answer = _urgency_answer(answers or {})
    if answer is None:
        return "low"
    position = _normalized_score(answer)
    if position < 0.20:
        index = 0
    elif position < 0.40:
        index = 1
    elif position < 0.60:
        index = 2
    elif position < 0.80:
        index = 3
    else:
        index = 4
    if answer_confidence(answer) < 0.5:
        index = max(0, index - 1)
    return _COST_TIERS[index]


def _urgency_answer(answers: dict) -> dict | None:
    for name in ("urgency", "difficulty"):
        answer = answers.get(name)
        if isinstance(answer, dict) and "score" in answer:
            return answer
    return None


def _normalized_score(answer: dict) -> float:
    try:
        score = float(answer.get("score"))
    except (TypeError, ValueError):
        return 0.0
    span = _score_span(answer, score)
    if span <= 0:
        return 0.0
    return max(0.0, min(1.0, score / span))


def _score_span(answer: dict, score: float) -> float:
    probs = answer.get("probabilities")
    if isinstance(probs, dict) and probs:
        indexes = []
        for key in probs:
            try:
                indexes.append(int(str(key)))
            except ValueError:
                continue
        if indexes:
            return float(max(indexes))
    if isinstance(probs, list) and len(probs) >= 2:
        return float(len(probs) - 1)
    return 2.0 if score > 1 else 1.0


def classify_route(answers: dict) -> tuple[str, str, float]:
    """Return ``(route, reason, confidence)``.

    ``route`` is ``deterministic`` or ``generative``.
    """
    confidence = routing_confidence(answers)
    needs = answers.get("needs_generation") if isinstance(answers, dict) else None
    if isinstance(needs, dict) and "noul" in needs:
        try:
            p_gen = float(needs["noul"])
        except (TypeError, ValueError):
            p_gen = 1.0
        if p_gen >= system1_needs_generation_threshold():
            return "generative", "needs_generation", confidence
    if confidence >= system1_high_confidence():
        return "deterministic", "high_confidence", confidence
    return "generative", "mid_or_low_confidence", confidence


def _as_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
