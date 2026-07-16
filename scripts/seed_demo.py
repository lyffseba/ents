#!/usr/bin/env python
"""
scripts/seed_demo.py - Populate demo data for testing + judge demos + submission evidence.
Run: python scripts/seed_demo.py --realistic
Creates users, progress, agent decisions (from running agents), fake revenue events (for export test).
Toggle --realistic for numbers you can screenshot for XPRIZE (disclose as demo or replace with live).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from datetime import datetime, timedelta
from web.deps import SessionLocal, engine, Base
from web import models
import random

Base.metadata.create_all(bind=engine)

def seed(demo_revenue: bool = False):
    db = SessionLocal()
    try:
        # Demo users (arms-length style)
        users = [
            models.User(email="alex@indie.ai", is_pro=True),
            models.User(email="sam.cs@uni.edu", is_pro=False),
            models.User(email="dev@bootcamp.io", is_pro=True),
        ]
        for u in users:
            db.merge(u)
        db.commit()

        # Progress
        for u in users:
            p = models.Progress(user_id=u.id, phase="01", pillars_completed="jax,mlx")
            db.add(p)
        
        # Simulate agent decisions (run agents first for real Gemini ones, or hardcode good ones)
        decisions = [
            models.AgentDecision(agent_name="RetentionAgent", decision="User sam.cs@uni.edu stalled 6d on softmax. Gemini: 'The probabilities are your compass in the dark forest.' Sent custom drill + 20% code.", gemini_prompt_summary="Stalled user on 01", gemini_output="...", action_taken="nudge_sent"),
            models.AgentDecision(agent_name="ContentAgent", decision="35% fail rate on exact softmax format -> proposed new JAX micro-exercise for Phase 01.", gemini_prompt_summary="failure patterns", gemini_output="New exercise: ...", action_taken="proposed"),
        ]
        for d in decisions:
            db.add(d)

        if demo_revenue:
            # Fake but realistic for testing export (replace with real Stripe data for submission)
            for m, amt in [("2026-05", 129.0), ("2026-06", 1450.0)]:
                ev = models.RevenueEvent(amount_usd=amt, month=m, source="stripe", is_related_party=False, user_email="alex@indie.ai")
                db.add(ev)
            # Related party separate
            db.add(models.RevenueEvent(amount_usd=29.0, month="2026-06", source="stripe", is_related_party=True, user_email="family@demo.test"))

        db.commit()
        print("✅ Demo data seeded. Run agents for live Gemini decisions. Use export_revenue.py for artifacts.")
    finally:
        db.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--realistic", action="store_true")
    args = ap.parse_args()
    seed(demo_revenue=args.realistic)
