"""
Server-side Oracle of Fangorn.

Grades one pillar via GRADE_PILLAR so a broken MAX file does not fail a JAX submit.
Paths come from max_env/phases/curriculum.json.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from .deps import call_gemini

PHASES_DIR = Path(__file__).parent.parent / "max_env" / "phases"
if str(PHASES_DIR) not in sys.path:
    sys.path.insert(0, str(PHASES_DIR))

from curriculum import grade_script, phase_dir, pillar_path  # noqa: E402


def run_local_grader(phase: str, pillar: str, code: str) -> dict:
    try:
        target = pillar_path(phase, pillar)
        grader = grade_script(phase)
    except KeyError:
        return {"passed": False, "output": f"Unknown phase/pillar {phase!r}/{pillar!r}."}

    if not grader.is_file():
        return {"passed": False, "output": f"No grader in {phase_dir(phase)}."}

    target.parent.mkdir(parents=True, exist_ok=True)
    backup = target.read_text() if target.exists() else None
    env = {**os.environ, "GRADE_PILLAR": pillar}
    try:
        target.write_text(code)
        result = subprocess.run(
            [f"./{grader.name}"],
            cwd=str(grader.parent),
            capture_output=True,
            text=True,
            timeout=90,
            env=env,
        )
        output = (result.stdout or "") + (result.stderr or "")
        passed = "✅ PASS" in output and "❌ FAIL" not in output
        return {"passed": passed, "output": output[-2000:], "pillar": pillar}
    except subprocess.TimeoutExpired:
        return {"passed": False, "output": "Oracle timed out after 90s."}
    finally:
        if backup is None:
            if target.exists():
                target.unlink()
        else:
            target.write_text(backup)


def ai_oracle_review(phase: str, pillar: str, code: str, auto_result: dict) -> str:
    prompt = f"""Phase {phase} {pillar} submission.
Auto Oracle result: {auto_result}
Student code (first 1500 chars):
{code[:1500]}

As the Oracle of Fangorn, give strict, encouraging feedback in 1-2 paragraphs.
Point out exact math issues vs SUBJECT.md. Suggest one next micro-exercise.
End with a lore quote. Never give the full solution on the first try."""
    return call_gemini(
        prompt,
        system="You are the ancient, no-nonsense Oracle of Fangorn.",
    )


def grade_submission(phase: str, pillar: str, code: str) -> dict:
    auto = run_local_grader(phase, pillar, code)
    ai_fb = ai_oracle_review(phase, pillar, code, auto)
    return {
        "auto": auto,
        "ai_feedback": ai_fb,
        "overall": "strong" if auto.get("passed") else "needs work (AI can help)",
    }
