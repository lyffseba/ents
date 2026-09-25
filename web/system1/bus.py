"""Run a System 1 pass, gate it, draft only when needed, and log the decision."""

from __future__ import annotations

import json
import os
from typing import Any

from ..config import (
    openrouter_api_key,
    openrouter_chat_url,
    system1_high_confidence,
    system1_jev_model,
    system2_model,
)
from .backends import laya_importable, predict, requested_backend
from .flows import draft_raw, get_flow, render_raw
from .gate import classify_route
from .questions import QuestionError, normalize_questions


def status() -> dict:
    """Backend selection without loading weights or calling the network."""
    setting = os.getenv("SYSTEM1_BACKEND", "").strip().lower()
    return {
        "setting": setting or "auto",
        "requested_backend": requested_backend(),
        "laya_importable": laya_importable(),
        "openrouter_configured": bool(openrouter_api_key()),
        "high_confidence": system1_high_confidence(),
        "jev_model": system1_jev_model(),
        "system2_model": system2_model(),
    }


def decide_flow(flow: str, state: Any) -> dict:
    """Score a named Academy flow (``tutor`` or ``retention``)."""
    try:
        spec = get_flow(flow)
    except KeyError as exc:
        raise QuestionError(str(exc)) from exc
    return decide(
        state,
        spec["questions"],
        flow=flow,
        render=spec["render"],
        draft=spec["draft"],
    )


def decide(
    state: Any,
    questions: dict,
    *,
    flow: str = "raw",
    render=None,
    draft=None,
) -> dict:
    """Score questions, gate on confidence, and log one System 1 row."""
    normalized = normalize_questions(questions)
    prediction = predict(state, normalized)
    answers = prediction["answers"]
    route, reason, confidence = classify_route(answers)
    provider = None
    if route == "deterministic":
        text = (render or render_raw)(state, answers)
    else:
        system, prompt = (draft or draft_raw)(state, answers, reason)
        text, provider = draft_text(system, prompt)
    outcome = {
        "text": text,
        "route": route,
        "reason": reason,
        "backend": prediction["backend"],
        "requested_backend": prediction["requested_backend"],
        "fallback_reason": prediction["fallback_reason"],
        "model": prediction.get("model"),
        "confidence": round(confidence, 4),
        "answers": answers,
        "generative_provider": provider,
        "flow": flow,
    }
    _log(outcome, state)
    return outcome


def draft_text(system: str, prompt: str) -> tuple[str, str]:
    """System 2 draft. OpenRouter chat when a key is set, otherwise demo-safe Gemini.

    No key skips the OpenRouter call entirely. The default chat model is
    ``openrouter/free`` (override with ``SYSTEM2_MODEL``).
    """
    if openrouter_api_key():
        try:
            return _openrouter_chat(system, prompt), "openrouter"
        except Exception as exc:
            print(f"[SYSTEM1] OpenRouter chat failed ({type(exc).__name__}: {exc}); using demo/gemini draft")
    text = _call_gemini(prompt, system)
    if text.startswith("[demo-gemini]"):
        return text, "demo"
    if text.startswith("[Gemini error"):
        return text, "gemini_error"
    return text, "gemini"


def _call_gemini(prompt: str, system: str) -> str:
    # Imported at call time so tests can patch web.deps.call_gemini.
    from ..deps import call_gemini
    return call_gemini(prompt, system)


def _openrouter_chat(system: str, prompt: str) -> str:
    import httpx

    response = httpx.post(
        openrouter_chat_url(),
        headers={
            "Authorization": f"Bearer {openrouter_api_key()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/lyffseba/ents",
            "X-OpenRouter-Title": "Ents Academy",
        },
        json={
            "model": system2_model(),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=30.0,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["choices"][0]["message"]["content"]


def _log(outcome: dict, state: Any) -> None:
    from ..agents.base import log_decision

    compact = _compact_answers(outcome["answers"])
    fallback = outcome.get("fallback_reason")
    decision = (
        f"flow={outcome['flow']} route={outcome['route']} reason={outcome['reason']} "
        f"backend={outcome['backend']} requested={outcome['requested_backend']} "
        f"conf={outcome['confidence']:.3f} {compact}"
    )
    if fallback:
        decision += f" fallback={fallback}"
    provider = outcome.get("generative_provider")
    if outcome["route"] == "deterministic":
        action = "system1:deterministic"
    else:
        action = f"system1:generative:{provider or 'unknown'}"
    summary = json.dumps(
        {"flow": outcome["flow"], "state": state_preview(state), "model": outcome.get("model")},
        default=str,
    )
    try:
        log_decision("System1", decision, summary, outcome["text"], action)
    except Exception as exc:
        print(f"[SYSTEM1] failed to log decision ({type(exc).__name__}: {exc})")


def state_preview(state: Any) -> str:
    if isinstance(state, str):
        return state[:240]
    try:
        return json.dumps(state, default=str)[:240]
    except TypeError:
        return str(state)[:240]


def _compact_answers(answers: dict) -> str:
    parts = []
    for name, answer in answers.items():
        if not isinstance(answer, dict):
            continue
        if "choice" in answer:
            parts.append(f"{name}={answer['choice']}@{float(answer.get('confidence') or 0):.2f}")
        elif "noul" in answer:
            parts.append(f"{name}={float(answer['noul']):.2f}")
        elif "score" in answer:
            parts.append(f"{name}={float(answer['score']):.2f}")
    return " ".join(parts)
