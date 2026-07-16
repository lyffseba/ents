"""
web/oracle.py - Server-side "Oracle of Fangorn" for web lab.
Reuses logic from max_env/phases/*/grademe.sh (string match + pixi run patterns).
Adds Gemini qualitative review on top (the AI layer for XPRIZE).
For full pillars: encourage local download + grademe.sh (the real Oracle).
JAX subset can run in-process for instant feedback.
"""

import subprocess
import os
from pathlib import Path
from .deps import call_gemini

PHASES_DIR = Path(__file__).parent.parent / "max_env" / "phases"

def run_local_grader(phase: str, pillar: str, code: str) -> dict:
    """Write temp code to the ex dir and invoke grademe.sh (like TUI does)."""
    # Security note: in prod, this should be heavily sandboxed (gvisor, firejail, or separate worker).
    # For MVP + contest demo we use temp files + trust (or limit to JAX).
    phase_dir = PHASES_DIR / {
        "00": "00_The_Seed",
        "01": "01_The_Enting",
        "02": "02_The_Lexicon",
    }.get(phase, "00_The_Seed")
    
    # Map pillar to exact file (simplified)
    pillar_map = {
        "jax": ("ex00_jax_soil/soil.py" if phase=="00" else "ex00_jax_bigram/bigram.py" if phase=="01" else "ex00_jax_lexicon/lexicon.py"),
        "max": ("ex02_max_roots/roots.py" if phase=="00" else "ex02_max_bigram/bigram_graph.py" if phase=="01" else "ex02_max_lexicon/lexicon_graph.py"),
    }
    target_rel = pillar_map.get(pillar, "ex00_jax_soil/soil.py")
    target = phase_dir / target_rel
    
    # Write user code (backup original? for demo we just run)
    backup = target.read_text() if target.exists() else ""
    try:
        target.write_text(code)
        # Invoke like grademe (cd + pixi run). This may be slow; real = pre-warmed worker.
        result = subprocess.run(
            ["./grademe.sh"],
            cwd=str(phase_dir),
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout + result.stderr
        passed = "✅ PASS" in output and "❌ FAIL" not in output
        return {"passed": passed, "output": output[:2000]}
    finally:
        if backup:
            target.write_text(backup)

def ai_oracle_review(phase: str, pillar: str, code: str, auto_result: dict) -> str:
    """Gemini layer on top of auto. This is a real LLM call in the deployed path."""
    prompt = f"""Phase {phase} {pillar} submission.
Auto Oracle result: {auto_result}
Student code (first 1500 chars):
{code[:1500]}

As the Oracle of Fangorn, give strict, encouraging feedback in 1-2 paragraphs. Point out exact math issues vs the spec in SUBJECT.md. Suggest one next micro-exercise. End with a lore quote."""
    return call_gemini(prompt, system="You are the ancient, no-nonsense Oracle of Fangorn. Never give full solutions on first try.")

def grade_submission(phase: str, pillar: str, code: str) -> dict:
    auto = run_local_grader(phase, pillar, code)
    ai_fb = ai_oracle_review(phase, pillar, code, auto)
    return {
        "auto": auto,
        "ai_feedback": ai_fb,
        "overall": "strong" if auto.get("passed") else "needs work (AI can help)"
    }
