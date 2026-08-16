"""
web/oracle.py - Server-side Oracle of Fangorn.

Runs the real module grademe.sh (no answer-echo fallbacks).
Gemini review is layered on top when a key is present; demo mode still grades.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .deps import call_gemini

PHASES_DIR = Path(__file__).parent.parent / "max_env" / "phases"

PHASE_DIRS = {
    "00": "C00_The_Seed",
    "01": "C01_The_Enting",
    "02": "C02_The_Lexicon",
}

PILLAR_FILES = {
    "00": {
        "jax": "ex00_jax_soil/soil.py",
        "mlx": "ex01_mlx_branch/branch.py",
        "max": "ex01_max_roots/roots.py",
        "mojo": "ex02_mojo_sprout/sprout.mojo",
    },
    "01": {
        "jax": "ex00_jax_bigram/bigram.py",
        "mlx": "ex01_mlx_leaf/leaf.py",
        "max": "ex01_max_bigram/bigram_graph.py",
        "mojo": "ex02_mojo_bigram/bigram.mojo",
    },
    "02": {
        "jax": "ex00_jax_lexicon/lexicon.py",
        "mlx": "ex01_mlx_lexicon/lexicon.py",
        "max": "ex02_max_lexicon/lexicon_graph.py",
        "mojo": "ex03_mojo_lexicon/tokenizer.mojo",
    },
}


def _grader_script(phase_dir: Path) -> Path | None:
    for name in ("grademe.sh", "grademe.xprize.sh"):
        candidate = phase_dir / name
        if candidate.exists():
            return candidate
    return None


def run_local_grader(phase: str, pillar: str, code: str) -> dict:
    """Write the submitted file, run the module Oracle, restore the original."""
    phase_dir = PHASES_DIR / PHASE_DIRS.get(phase, "C00_The_Seed")
    files = PILLAR_FILES.get(phase, PILLAR_FILES["00"])
    target_rel = files.get(pillar)
    if not target_rel:
        return {"passed": False, "output": f"Unknown pillar {pillar!r} for phase {phase!r}."}

    target = phase_dir / target_rel
    grader = _grader_script(phase_dir)
    if grader is None:
        return {"passed": False, "output": f"No grader in {phase_dir}."}

    target.parent.mkdir(parents=True, exist_ok=True)
    backup = target.read_text() if target.exists() else None
    try:
        target.write_text(code)
        result = subprocess.run(
            [f"./{grader.name}"],
            cwd=str(phase_dir),
            capture_output=True,
            text=True,
            timeout=90,
        )
        output = (result.stdout or "") + (result.stderr or "")
        passed = "✅ PASS" in output and "❌ FAIL" not in output
        return {"passed": passed, "output": output[-2000:]}
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
