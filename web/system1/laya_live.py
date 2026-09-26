"""Opt-in smoke for the local Laya System 1 backend.

Default tests do not run this module and do not download weights.

    python -m web.system1.laya_live --fixture   # adapter path, no Hub download
    python -m web.system1.laya_live             # real laya.Router.predict

``--fixture`` feeds a recorded Router result through the same bus the tutor
uses, so you can see ``backend=laya`` without the checkpoint. The real
command pins ``SYSTEM1_BACKEND=laya`` and exits 1 when the process falls
back to the mock. It never calls the OpenRouter decisions or chat APIs.
"""

from __future__ import annotations

import json
import os
import sys

from ..config import system1_laya_device, system1_laya_model, system1_laya_repo
from .backends import predict, reset_backend_state
from .bus import decide_flow

USAGE = """\
usage: python -m web.system1.laya_live [--fixture]

Pins SYSTEM1_BACKEND=laya for this process.
--fixture runs the tutor gate on a recorded Router result (no download).
Without --fixture, calls laya.Router.predict. Exit 1 if that falls back to mock.

Optional:
  SYSTEM1_LAYA_MODEL     english | multilingual | typed-decisions (aliases ok)
  SYSTEM1_LAYA_DEVICE    cpu | cuda | mps
  SYSTEM1_LAYA_PATH      local checkpoint directory (skips the Hub download)
  SYSTEM1_LAYA_REPO      default convaiinnovations/laya
  SYSTEM1_LAYA_REVISION  Hub commit, branch, or tag
  SYSTEM1_LAYA_PRELOAD   1 to build checkpoints at startup
  SYSTEM1_LAYA_MAX_LEN   passed to Router.predict
  SYSTEM1_LAYA_AUTO_TASK 1 to allow automatic typed-decisions routing
  SYSTEM1_LAYA_TOKEN     optional; else HF_TOKEN. The public model needs neither.
"""

SMOKE_STATE = "Please refund the duplicate invoice payment."

SMOKE_QUESTIONS = {
    "department": {
        "type": "choice",
        "instructions": "Which department should handle this?",
        "criteria": {
            "billing": "invoices payments refunds",
            "technical": "bugs outages crashes",
        },
    },
    "needs_generation": {
        "type": "noul",
        "instructions": "Does this case need a personalized written message instead of a fixed template?",
    },
}

_FIXTURE_RESULT = {
    "answers": {
        "intent": {
            "choice": "define",
            "confidence": 0.97,
            "probabilities": {"define": 0.97, "hint": 0.01, "lore": 0.01, "open": 0.01},
        },
        "difficulty": {"score": 0.1, "confidence": 0.9, "probabilities": [0.9, 0.1, 0.0]},
        "needs_generation": {"noul": 0.04, "confidence": 0.93},
    },
    "routing": {
        "model": "english",
        "repo": "convaiinnovations/laya",
        "reason": "fixture (no weights loaded)",
    },
}


class _FixtureRouter:
    def predict(self, state, questions, **kwargs):
        return _FIXTURE_RESULT


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if any(arg in {"-h", "--help"} for arg in args):
        if args not in (["-h"], ["--help"]):
            print(USAGE, end="", file=sys.stderr)
            return 2
        print(USAGE, end="")
        return 0
    if args == ["--fixture"]:
        return _fixture()
    if args:
        print(f"unknown arguments: {' '.join(args)}", file=sys.stderr)
        print(USAGE, end="", file=sys.stderr)
        return 2
    return _live()


def _fixture() -> int:
    from . import laya as laya_runtime

    os.environ["SYSTEM1_BACKEND"] = "laya"
    reset_backend_state()
    original = laya_runtime.open_router
    laya_runtime.open_router = lambda: _FixtureRouter()
    try:
        outcome = decide_flow("tutor", {"question": "What is softmax?"})
    finally:
        laya_runtime.open_router = original
        reset_backend_state()
    report = {
        "backend": outcome["backend"],
        "requested_backend": outcome["requested_backend"],
        "model": outcome.get("model"),
        "route": outcome["route"],
        "reason": outcome["reason"],
        "fallback_reason": outcome.get("fallback_reason"),
        "answers": outcome["answers"],
        "text": outcome["text"],
        "fixture": True,
    }
    print(json.dumps(report, indent=2))
    if outcome.get("backend") != "laya" or outcome.get("route") != "deterministic":
        print("laya fixture did not take the deterministic Laya path", file=sys.stderr)
        return 1
    return 0


def _live() -> int:
    os.environ["SYSTEM1_BACKEND"] = "laya"
    reset_backend_state()
    result = predict(SMOKE_STATE, SMOKE_QUESTIONS)
    if result.get("backend") != "laya":
        print(f"laya fallback: {result.get('fallback_reason')}", file=sys.stderr)
        return 1
    report = {
        "backend": result["backend"],
        "requested_backend": result["requested_backend"],
        "model": result.get("model"),
        "laya_repo": system1_laya_repo(),
        "laya_model": system1_laya_model() or "auto",
        "laya_device": system1_laya_device() or "auto",
        "answers": result["answers"],
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
