"""
RetentionAgent: Scans for stalled learners, uses Gemini to craft personalized intervention.
This executes a *key business decision* autonomously. Logged.
Run via scheduler or manually for demos.
"""
from datetime import datetime, timedelta
from ..deps import SessionLocal, call_gemini
from .base import log_decision
from .. import models

def run_retention_agent(dry_run: bool = False):
    db = SessionLocal()
    try:
        # In real: query users with last_progress < 5 days ago and phase > 0
        # For MVP: simulate or use demo data
        stalled = [
            {"id": 42, "email": "slow@ent.dev", "phase": "01", "days": 7, "stuck_on": "softmax edge cases"},
        ]
        for u in stalled:
            prompt = f"User {u['id']} ({u['email']}) has been at phase {u['phase']} for {u['days']} days, stuck on: {u['stuck_on']}. Write a short encouraging nudge (2 sentences) + one specific micro-hint from the Fangorn Trials. Offer 20% off Pro if appropriate."
            nudge = call_gemini(prompt, system="You are the Entmoot Retention Agent. Be wise, ancient, and data-driven.")
            
            decision = f"Stalled user #{u['id']} at {u['phase']}. Action: send nudge + discount offer."
            log_decision("RetentionAgent", decision, prompt, nudge, "email_nudge_sent" if not dry_run else "dry_run")
            
            if not dry_run:
                print(f"[RETENTION] Would email: {nudge}")
            else:
                print(f"[RETENTION DRY] {nudge}")
    finally:
        db.close()

if __name__ == "__main__":
    run_retention_agent(dry_run=True)
