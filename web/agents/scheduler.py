"""
Simple APScheduler for background agents. In prod on Cloud Run: either in-process (single instance) or better: Cloud Scheduler -> separate lightweight Run job that hits /internal/run-agents.
For contest demo: in-process is fine and shows "continuously running".
"""
from apscheduler.schedulers.background import BackgroundScheduler
from .retention import run_retention_agent
from .content import run_content_agent

scheduler = BackgroundScheduler()

def start_agents():
    scheduler.add_job(run_retention_agent, 'interval', hours=6, id='retention', replace_existing=True)
    scheduler.add_job(run_content_agent, 'interval', hours=12, id='content', replace_existing=True)
    scheduler.start()
    print("✅ Entmoot Agents scheduler started (Retention every 6h, Content every 12h)")

def stop_agents():
    scheduler.shutdown(wait=False)
