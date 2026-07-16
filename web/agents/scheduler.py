"""
Background agents for contest evidence.
Cloud Run: in-process scheduler is fine for single-instance demos.
Production scale: Cloud Scheduler -> POST /ops/trigger-*.
"""
from __future__ import annotations

import os
from apscheduler.schedulers.background import BackgroundScheduler

from .retention import run_retention_agent
from .content import run_content_agent

scheduler = BackgroundScheduler()
_started = False


def start_agents():
    global _started
    if os.getenv("ENTS_DISABLE_SCHEDULER", "").lower() in {"1", "true", "yes"}:
        print("ℹ️ Scheduler disabled (ENTS_DISABLE_SCHEDULER)")
        return
    if _started or scheduler.running:
        return
    scheduler.add_job(
        run_retention_agent,
        "interval",
        hours=6,
        id="retention",
        replace_existing=True,
    )
    scheduler.add_job(
        run_content_agent,
        "interval",
        hours=12,
        id="content",
        replace_existing=True,
    )
    scheduler.start()
    _started = True
    print("✅ Entmoot Agents scheduler started (Retention 6h, Content 12h)")


def stop_agents():
    global _started
    if scheduler.running:
        scheduler.shutdown(wait=False)
    _started = False
