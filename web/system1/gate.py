"""Pure confidence policy. No network, no database."""

from __future__ import annotations

from ..config import system1_high_confidence, system1_needs_generation_threshold


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
