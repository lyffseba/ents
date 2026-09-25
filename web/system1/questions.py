"""Normalize Choice / Score / Noul questions onto Laya's wire shape."""

from __future__ import annotations

_TYPE_MAP = {
    "choice": "choice",
    "score": "score",
    "noul": "noul",
}


class QuestionError(ValueError):
    """Caller sent a question the bus cannot score."""


def normalize_questions(questions: dict) -> dict:
    """Return ``{name: {type, instructions, criteria?}}`` with lowercase types.

    Accepts ``Choice``, ``Score``, and ``Noul`` (Laya's ``choice`` / ``score``
    / ``noul``). Choice criteria may be a label→description map or a list of
    labels. Score criteria is an ordered list. Noul criteria are optional.
    """
    if not isinstance(questions, dict) or not questions:
        raise QuestionError("questions must be a non-empty object")

    normalized: dict = {}
    for name, raw in questions.items():
        if not isinstance(raw, dict):
            raise QuestionError(f"{name}: question must be an object")
        qtype = _TYPE_MAP.get(str(raw.get("type", "")).strip().lower())
        if qtype is None:
            raise QuestionError(f"{name}: type must be choice, score, or noul")
        instructions = str(raw.get("instructions") or "").strip()
        if not instructions:
            raise QuestionError(f"{name}: instructions are required")

        item: dict = {"type": qtype, "instructions": instructions}
        if raw.get("criteria") is not None:
            item["criteria"] = raw["criteria"]
        if raw.get("labels") is not None:
            item["labels"] = raw["labels"]

        if qtype == "choice" and not isinstance(item.get("criteria"), (dict, list)):
            raise QuestionError(f"{name}: choice requires criteria (object or list)")
        if qtype == "choice" and isinstance(item["criteria"], (dict, list)) and not item["criteria"]:
            raise QuestionError(f"{name}: choice criteria must not be empty")
        if qtype == "score" and not isinstance(item.get("criteria"), list):
            raise QuestionError(f"{name}: score requires criteria as an ordered list")
        if qtype == "score" and len(item["criteria"]) < 2:
            raise QuestionError(f"{name}: score criteria need at least two levels")

        normalized[str(name)] = item
    return normalized
