"""
RetentionAgent: Scans for stalled learners, uses Gemini to craft personalized intervention.
This executes a *key business decision* autonomously. Logged.
Run via scheduler or manually for demos.
"""
from ..deps import SessionLocal
from .base import log_decision
from ..system1 import decide_flow
from ..system1.flows import retention_state

def run_retention_agent(dry_run: bool = False):
    db = SessionLocal()
    try:
        # In real: query users with last_progress < 5 days ago and phase > 0
        # For MVP: simulate or use demo data
        stalled = [
            {"id": 42, "email": "slow@ent.dev", "phase": "01", "days": 7, "stuck_on": "softmax edge cases"},
        ]
        for u in stalled:
            state = retention_state(u)
            outcome = decide_flow("retention", state)
            nudge = outcome["text"]
            decision = (
                f"Stalled user #{u['id']} at {u['phase']}. "
                f"System1 route={outcome['route']} backend={outcome['backend']} "
                f"conf={outcome['confidence']:.2f} action={outcome['answers'].get('intervention', {}).get('choice')}."
            )
            log_decision(
                "RetentionAgent",
                decision,
                state["text"],
                nudge,
                "email_nudge_sent" if not dry_run else "dry_run",
            )

            if not dry_run:
                print(f"[RETENTION] Would email: {nudge}")
            else:
                print(f"[RETENTION DRY] {nudge}")
    finally:
        db.close()

if __name__ == "__main__":
    run_retention_agent(dry_run=True)
