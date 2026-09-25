"""Opt-in live smoke for OpenRouter Jev and a System 2 chat draft.

Default CI does not run this module. It talks to OpenRouter only when
``OPENROUTER_API_KEY`` is set and someone invokes it:

    python -m web.system1.live
    python -m web.system1.live --draft

The command forces ``SYSTEM1_BACKEND=openrouter_jev`` so a mock setting in
the shell cannot hide a failed live call. ``--draft`` also calls chat
completions. System 2 default is ``openrouter/auto``; set
``SYSTEM2_MODEL=openrouter/free`` for the zero-cost lane. Without the
flag, only the Jev decision is sent. Jev never uses the Auto chat model.
"""

from __future__ import annotations

import json
import os
import sys

from ..config import SYSTEM2_AUTO_MODEL, openrouter_api_key, system1_jev_model, system2_model
from .backends import predict
from .bus import draft_text
from .gate import auto_cost_tier

USAGE = """\
usage: python -m web.system1.live [--draft]

Reads OPENROUTER_API_KEY from the environment (required).
Pins SYSTEM1_BACKEND=openrouter_jev for this process.
Optional: SYSTEM1_JEV_MODEL (default typesafe/jev-1.13; chat ids are rejected),
          SYSTEM2_MODEL (default openrouter/auto; or openrouter/free, or a :free id),
          SYSTEM2_COST_TIER (low|medium|high|xhigh|max; default maps urgency, else low).
--draft calls chat completions. Jev stays on the decisions API.
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


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if any(arg in {"-h", "--help"} for arg in args):
        print(USAGE, end="")
        return 0
    unknown = [arg for arg in args if arg != "--draft"]
    if unknown:
        print(f"unknown arguments: {' '.join(unknown)}", file=sys.stderr)
        print(USAGE, end="", file=sys.stderr)
        return 2
    if not openrouter_api_key():
        print("OPENROUTER_API_KEY is unset; live OpenRouter smoke skipped.", file=sys.stderr)
        return 2

    os.environ["SYSTEM1_BACKEND"] = "openrouter_jev"
    result = predict(SMOKE_STATE, SMOKE_QUESTIONS)
    if result.get("backend") != "openrouter_jev":
        print(f"jev fallback: {result.get('fallback_reason')}", file=sys.stderr)
        return 1

    tier = auto_cost_tier(result["answers"]) if system2_model() == SYSTEM2_AUTO_MODEL else None
    report = {
        "backend": result["backend"],
        "jev_model": system1_jev_model(),
        "served_model": result.get("model"),
        "system2_model": system2_model(),
        "cost_tier": tier,
        "answers": result["answers"],
        "draft": None,
    }
    if "--draft" in args:
        system = "You are Treebeard. Reply in one short sentence. Do not invent charges."
        prompt = (
            "System 1 escalated for a live smoke.\n"
            f"State: {SMOKE_STATE}\n"
            f"Answers: {json.dumps(result['answers'], default=str)}\n"
            "Write one sentence the Academy can show an operator."
        )
        text, provider, meta = draft_text(system, prompt, answers=result["answers"], state=SMOKE_STATE)
        report["draft"] = {
            "provider": provider,
            "model": meta.get("requested_model") or system2_model(),
            "served_model": meta.get("served_model"),
            "cost_tier": meta.get("cost_tier"),
            "text": text,
        }
        print(json.dumps(report, indent=2))
        if provider != "openrouter" or not str(text).strip():
            print("system 2 draft did not use OpenRouter", file=sys.stderr)
            return 1
        return 0

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
