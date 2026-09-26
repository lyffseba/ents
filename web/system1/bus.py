"""Run a System 1 pass, gate it, draft only when needed, and log the decision."""

from __future__ import annotations

import json
import os
from typing import Any

from ..config import (
    SYSTEM2_AUTO_MODEL,
    openrouter_api_key,
    openrouter_chat_url,
    system1_high_confidence,
    system1_jev_model,
    system1_laya_device,
    system1_laya_model,
    system1_laya_path,
    system1_laya_repo,
    system2_model,
)
from .backends import laya_importable, predict, requested_backend
from .flows import draft_raw, get_flow, render_raw
from .gate import auto_cost_tier, classify_route
from .questions import QuestionError, normalize_questions


def status() -> dict:
    """Backend selection without loading weights or calling the network."""
    setting = os.getenv("SYSTEM1_BACKEND", "").strip().lower()
    return {
        "setting": setting or "auto",
        "requested_backend": requested_backend(),
        "laya_importable": laya_importable(),
        "laya_model": system1_laya_model() or "auto",
        "laya_repo": system1_laya_repo(),
        "laya_device": system1_laya_device() or "auto",
        "laya_path": system1_laya_path() or None,
        "openrouter_configured": bool(openrouter_api_key()),
        "high_confidence": system1_high_confidence(),
        "jev_model": system1_jev_model(),
        "system2_model": system2_model(),
    }


def decide_flow(flow: str, state: Any, *, session_id: str | None = None) -> dict:
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
        session_id=session_id,
    )


def decide(
    state: Any,
    questions: dict,
    *,
    flow: str = "raw",
    render=None,
    draft=None,
    session_id: str | None = None,
) -> dict:
    """Score questions, gate on confidence, and log one System 1 row."""
    normalized = normalize_questions(questions)
    prediction = predict(state, normalized)
    answers = prediction["answers"]
    route, reason, confidence = classify_route(answers)
    provider = None
    draft_meta = {
        "requested_model": None,
        "served_model": None,
        "cost_tier": None,
        "session_id": None,
    }
    if route == "deterministic":
        text = (render or render_raw)(state, answers)
    else:
        system, prompt = (draft or draft_raw)(state, answers, reason)
        text, provider, draft_meta = draft_text(
            system,
            prompt,
            answers=answers,
            state=state,
            session_id=session_id,
        )
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
        "system2_model": draft_meta.get("requested_model"),
        "cost_tier": draft_meta.get("cost_tier"),
        "session_id": draft_meta.get("session_id"),
        "draft_model": draft_meta.get("served_model"),
    }
    _log(outcome, state)
    return outcome


def draft_text(
    system: str,
    prompt: str,
    *,
    answers: dict | None = None,
    state: Any = None,
    session_id: str | None = None,
) -> tuple[str, str, dict]:
    """System 2 draft. OpenRouter chat when a key is set, otherwise demo-safe Gemini.

    No key skips the OpenRouter call. The default chat model is
    ``openrouter/auto``. ``openrouter/free`` is the zero-cost override.
    Auto requests send plugin ``auto-router`` with a ``cost_tier``.
    ``session_id`` is the explicit argument when set, otherwise one taken
    from the state. Typed System 1 calls never come through here.
    """
    meta = {
        "requested_model": None,
        "served_model": None,
        "cost_tier": None,
        "session_id": None,
    }
    if openrouter_api_key():
        body = _chat_request(system, prompt, answers, state, session_id=session_id)
        meta["requested_model"] = body["model"]
        meta["session_id"] = body.get("session_id")
        plugins = body.get("plugins") or []
        if plugins:
            meta["cost_tier"] = plugins[0].get("cost_tier")
        try:
            text, served = _openrouter_chat(body)
            meta["served_model"] = served
            return text, "openrouter", meta
        except Exception as exc:
            print(f"[SYSTEM1] OpenRouter chat failed ({type(exc).__name__}: {exc}); using demo/gemini draft")
    text = _call_gemini(prompt, system)
    if text.startswith("[demo-gemini]"):
        return text, "demo", meta
    if text.startswith("[Gemini error"):
        return text, "gemini_error", meta
    return text, "gemini", meta


def session_id_from_state(state: Any) -> str | None:
    """Conversation id for Auto stickiness, when the state actually has one."""
    if not isinstance(state, dict):
        return None
    for key in ("session_id", "sessionId", "session"):
        value = state.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:200]
        if isinstance(value, int) and not isinstance(value, bool):
            return str(value)
    learner = state.get("id")
    if isinstance(learner, bool) or learner is None:
        return None
    if isinstance(learner, (int, str)) and str(learner).strip():
        if any(key in state for key in ("email", "phase", "stuck_on")):
            return f"learner:{learner}"
    return None


def resolve_session_id(explicit: str | None, state: Any) -> str | None:
    """Stickiness key. An explicit id wins; otherwise read one from ``state``."""
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()[:200]
    return session_id_from_state(state)


def _chat_request(
    system: str,
    prompt: str,
    answers: dict | None,
    state: Any,
    *,
    session_id: str | None = None,
) -> dict:
    model = system2_model()
    body: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }
    session = resolve_session_id(session_id, state)
    if session:
        body["session_id"] = session
    if model == SYSTEM2_AUTO_MODEL:
        body["plugins"] = [{
            "id": "auto-router",
            "cost_tier": auto_cost_tier(answers if isinstance(answers, dict) else {}),
        }]
    return body


def _call_gemini(prompt: str, system: str) -> str:
    # Imported at call time so tests can patch web.deps.call_gemini.
    from ..deps import call_gemini
    return call_gemini(prompt, system)


def _openrouter_chat(body: dict) -> tuple[str, str | None]:
    import httpx

    response = httpx.post(
        openrouter_chat_url(),
        headers={
            "Authorization": f"Bearer {openrouter_api_key()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/lyffseba/ents",
            "X-OpenRouter-Title": "Ents Academy",
        },
        json=body,
        timeout=30.0,
    )
    response.raise_for_status()
    payload = response.json()
    content = payload["choices"][0]["message"]["content"]
    served = payload.get("model") if isinstance(payload, dict) else None
    return content, (str(served) if served else None)


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
    if outcome.get("system2_model"):
        decision += f" system2={outcome['system2_model']}"
    if outcome.get("cost_tier"):
        decision += f" tier={outcome['cost_tier']}"
    if outcome.get("session_id"):
        decision += f" session={outcome['session_id']}"
    if outcome.get("draft_model"):
        decision += f" draft_model={outcome['draft_model']}"
    provider = outcome.get("generative_provider")
    if outcome["route"] == "deterministic":
        action = "system1:deterministic"
    else:
        action = f"system1:generative:{provider or 'unknown'}"
    # Routed model leads so the stored summary keeps response.model if truncated.
    summary = json.dumps(
        {
            "draft_model": outcome.get("draft_model"),
            "model": outcome.get("draft_model") or outcome.get("model"),
            "system1_model": outcome.get("model"),
            "cost_tier": outcome.get("cost_tier"),
            "session_id": outcome.get("session_id"),
            "flow": outcome["flow"],
            "state": state_preview(state),
        },
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
