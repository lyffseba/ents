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

from fastapi.testclient import TestClient
from web.app import app

client = TestClient(app)


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

    # Tutor POST (demo gemini)
    r = client.post("/tutor/ask", data={"question": "What is softmax?"})
    print(f"{'OK' if r.status_code == 200 else 'FAIL'} POST /tutor/ask -> {r.status_code}")
    if r.status_code != 200:
        failed += 1
    else:
        body = r.json()
        assert "answer" in body, body
        print("  answer[:80]=", body["answer"][:80])

    # Agent triggers (demo gemini + DB log)
    for path in ("/ops/trigger-retention", "/ops/trigger-content"):
        r = client.post(path)
        print(f"{'OK' if r.status_code == 200 else 'FAIL'} POST {path} -> {r.status_code}")
        if r.status_code != 200:
            failed += 1
            print(r.text[:300])

    r = client.get("/ops")
    print(f"{'OK' if r.status_code == 200 else 'FAIL'} GET /ops after triggers -> {r.status_code}")

    if failed:
        print(f"\n{failed} check(s) failed")
        return 1
    print("\nAll smoke checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
