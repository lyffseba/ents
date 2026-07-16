"""
Base for Gemini agents. Every agent must:
- Use call_gemini (logs the call + decision for evidence)
- Record AgentDecision row
- Be runnable on schedule (APScheduler or Cloud Scheduler)
This is what makes the business "operated by AI".
"""
from datetime import datetime
from ..deps import SessionLocal
from .. import models

def log_decision(agent_name: str, decision: str, prompt_summary: str, gemini_output: str, action: str):
    db = SessionLocal()
    try:
        rec = models.AgentDecision(
            agent_name=agent_name,
            decision=decision,
            gemini_prompt_summary=prompt_summary[:500],
            gemini_output=gemini_output[:2000],
            action_taken=action,
        )
        db.add(rec)
        db.commit()
        print(f"[AGENT_LOG] {agent_name}: {decision[:80]}...")
    finally:
        db.close()
