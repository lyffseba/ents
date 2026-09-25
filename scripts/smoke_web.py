#!/usr/bin/env python3
"""Smoke-test Ents Academy FastAPI surface without external Gemini keys."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["ENTS_DISABLE_SCHEDULER"] = "1"
os.environ["GEMINI_API_KEY"] = ""  # force demo mode (no live network)
os.environ["USE_VERTEX"] = "false"
os.environ["SYSTEM1_BACKEND"] = "mock"
os.environ["OPENROUTER_API_KEY"] = ""

from fastapi.testclient import TestClient
from web.app import app
from web import deps
from web.agents import content as content_agent
from web.system1.backends import predict, reset_backend_state
from web.system1.questions import normalize_questions

client = TestClient(app)

_gemini_calls = {"n": 0}
_real_gemini = deps.call_gemini


def _counting_gemini(prompt: str, system: str = "") -> str:
    _gemini_calls["n"] += 1
    return _real_gemini(prompt, system)


deps.call_gemini = _counting_gemini
content_agent.call_gemini = _counting_gemini


def main() -> int:
    checks = [
        ("GET", "/healthz", 200),
        ("GET", "/health", 200),
        ("GET", "/", 200),
        ("GET", "/ops", 200),
        ("GET", "/tutor", 200),
        ("GET", "/judges", 200),
        ("GET", "/pricing", 200),
        ("GET", "/dashboard", 200),
        ("GET", "/lab/00/jax", 200),
    ]
    failed = 0
    for method, path, want in checks:
        r = client.request(method, path)
        ok = r.status_code == want
        print(f"{'OK' if ok else 'FAIL'} {method} {path} -> {r.status_code}")
        if not ok:
            failed += 1
            print(r.text[:300])

    tutor_page = client.get("/tutor")
    tutor_ok = tutor_page.status_code == 200 and "System 1" in tutor_page.text
    print(f"{'OK' if tutor_ok else 'FAIL'} GET /tutor explains the System 1 gate")
    if not tutor_ok:
        failed += 1

    r = client.get("/system1/status")
    print(f"{'OK' if r.status_code == 200 else 'FAIL'} GET /system1/status -> {r.status_code}")
    if r.status_code != 200 or r.json().get("requested_backend") != "mock":
        failed += 1
        print(r.text[:300])
    else:
        print("  backend=", r.json().get("requested_backend"))

    # High-confidence tutor question: deterministic glossary, no generative call.
    before = _gemini_calls["n"]
    r = client.post("/tutor/ask", data={"question": "What is softmax?"})
    print(f"{'OK' if r.status_code == 200 else 'FAIL'} POST /tutor/ask (softmax) -> {r.status_code}")
    if r.status_code != 200:
        failed += 1
    else:
        body = r.json()
        gate = body.get("system1") or {}
        ok = (
            "answer" in body
            and gate.get("route") == "deterministic"
            and gate.get("backend") == "mock"
            and gate.get("generative_provider") is None
            and "softmax" in body["answer"].lower()
            and not body["answer"].startswith("[demo-gemini]")
            and _gemini_calls["n"] == before
        )
        print(f"{'OK' if ok else 'FAIL'} softmax gate route={gate.get('route')} conf={gate.get('confidence')} gemini_calls={_gemini_calls['n'] - before}")
        if not ok:
            failed += 1
            print(body)

    # Ambiguous ask escalates to the demo draft (no API key required).
    before = _gemini_calls["n"]
    r = client.post("/tutor/ask", data={"question": "???"})
    print(f"{'OK' if r.status_code == 200 else 'FAIL'} POST /tutor/ask (ambiguous) -> {r.status_code}")
    if r.status_code != 200:
        failed += 1
    else:
        body = r.json()
        gate = body.get("system1") or {}
        ok = (
            gate.get("route") == "generative"
            and gate.get("generative_provider") == "demo"
            and body["answer"].startswith("[demo-gemini]")
            and _gemini_calls["n"] == before + 1
        )
        print(f"{'OK' if ok else 'FAIL'} ambiguous gate route={gate.get('route')} provider={gate.get('generative_provider')}")
        if not ok:
            failed += 1
            print(body)

    # Choice / Score / Noul spellings and a confident raw decision.
    r = client.post("/system1/decide", json={
        "state": "Please refund the duplicate invoice payment",
        "questions": {
            "department": {
                "type": "Choice",
                "instructions": "Which department should handle this?",
                "criteria": {
                    "billing": "invoices payments refunds",
                    "technical": "bugs outages crashes",
                },
            },
            "urgency": {
                "type": "Score",
                "instructions": "How urgent is this request?",
                "criteria": ["not urgent", "soon", "critical deadline or blocking issue"],
            },
            "needs_generation": {
                "type": "Noul",
                "instructions": "Does this case need a personalized written message instead of a fixed template?",
            },
        },
    })
    print(f"{'OK' if r.status_code == 200 else 'FAIL'} POST /system1/decide (billing) -> {r.status_code}")
    if r.status_code != 200:
        failed += 1
        print(r.text[:400])
    else:
        body = r.json()
        dept = (body.get("answers") or {}).get("department") or {}
        ok = body.get("route") == "deterministic" and dept.get("choice") == "billing" and "billing" in body.get("text", "")
        print(f"{'OK' if ok else 'FAIL'} billing choice={dept.get('choice')} route={body.get('route')} conf={body.get('confidence')}")
        if not ok:
            failed += 1
            print(body)

    r = client.post("/system1/decide", json={"state": "hello"})
    print(f"{'OK' if r.status_code == 400 else 'FAIL'} POST /system1/decide (missing questions) -> {r.status_code}")
    if r.status_code != 400:
        failed += 1

    # Title-case normalization unit (no HTTP).
    try:
        normalized = normalize_questions({
            "keep": {"type": "Choice", "instructions": "Which?", "criteria": {"a": "one", "b": "two"}},
        })
        assert normalized["keep"]["type"] == "choice"
        print("OK normalize Choice -> choice")
    except Exception as exc:
        failed += 1
        print("FAIL normalize", exc)

    # Jev without a key, and Laya when the package is missing, both fall back to mock.
    reset_backend_state()
    os.environ["SYSTEM1_BACKEND"] = "openrouter_jev"
    os.environ["OPENROUTER_API_KEY"] = ""
    jev = predict("Please refund the duplicate invoice", {
        "department": {
            "type": "choice",
            "instructions": "Which department?",
            "criteria": {"billing": "invoices payments refunds", "technical": "bugs outages"},
        }
    })
    jev_ok = jev["backend"] == "mock" and jev["requested_backend"] == "openrouter_jev" and jev["fallback_reason"]
    print(f"{'OK' if jev_ok else 'FAIL'} openrouter_jev fallback reason={jev['fallback_reason']}")
    if not jev_ok:
        failed += 1

    reset_backend_state()
    try:
        import laya  # noqa: F401
        laya_present = True
    except ImportError:
        laya_present = False
    if not laya_present:
        os.environ["SYSTEM1_BACKEND"] = "laya"
        laya_result = predict("What is softmax?", {
            "intent": {
                "type": "choice",
                "instructions": "What kind of help?",
                "criteria": {"define": "softmax embedding", "open": "generated explanation"},
            }
        })
        laya_ok = (
            laya_result["backend"] == "mock"
            and laya_result["requested_backend"] == "laya"
            and laya_result["fallback_reason"]
        )
        print(f"{'OK' if laya_ok else 'FAIL'} laya fallback reason={laya_result['fallback_reason']}")
        if not laya_ok:
            failed += 1
    else:
        print("OK laya importable; skip missing-package fallback")
    reset_backend_state()
    os.environ["SYSTEM1_BACKEND"] = "mock"
    os.environ["OPENROUTER_API_KEY"] = ""

    # Agent triggers. Retention is gated (no generative call). Content still drafts.
    before = _gemini_calls["n"]
    r = client.post("/ops/trigger-retention")
    print(f"{'OK' if r.status_code == 200 else 'FAIL'} POST /ops/trigger-retention -> {r.status_code}")
    retention_skipped = _gemini_calls["n"] == before
    print(f"{'OK' if retention_skipped else 'FAIL'} retention skipped generative call (delta={_gemini_calls['n'] - before})")
    if r.status_code != 200 or not retention_skipped:
        failed += 1
        print(r.text[:300])

    before = _gemini_calls["n"]
    r = client.post("/ops/trigger-content")
    print(f"{'OK' if r.status_code == 200 else 'FAIL'} POST /ops/trigger-content -> {r.status_code}")
    content_drafted = _gemini_calls["n"] == before + 1
    print(f"{'OK' if content_drafted else 'FAIL'} content still drafts (delta={_gemini_calls['n'] - before})")
    if r.status_code != 200 or not content_drafted:
        failed += 1
        print(r.text[:300])

    r = client.get("/ops")
    ops_ok = r.status_code == 200 and "SYSTEM 1" in r.text and "flow=retention" in r.text and "route=deterministic" in r.text
    print(f"{'OK' if ops_ok else 'FAIL'} GET /ops shows System 1 retention decision -> {r.status_code}")
    if not ops_ok:
        failed += 1
        print(r.text[:500])

    if failed:
        print(f"\n{failed} check(s) failed")
        return 1
    print("\nAll smoke checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
