"""
web/config.py - Configuration for Ents Academy (XPRIZE contest platform).
Uses env vars for secrets. Keep this minimal and 12-factor.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = BASE_DIR.parent

# App
APP_NAME = "Ents Academy"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-prod-for-xprize")

# DB (sqlite for fast MVP dev + judge demos; prod -> postgres via Cloud SQL)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'ents_academy.db'}")

# Gemini (MANDATORY: at least one call in deployed app per rules. Use Vertex or generativeai)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
USE_VERTEX = os.getenv("USE_VERTEX", "false").lower() == "true"  # Set true for full Google Cloud Vertex AI
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")  # Or gemini-2.0-flash etc. Update per google-genai availability.

# Stripe (for real revenue evidence: total, by month, costs, mktg spend)
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")  # Use live for real revenue
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_...")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_...")
PRO_PRICE_ID = os.getenv("PRO_PRICE_ID", "price_...")  # Create in Stripe dashboard

# Google Cloud / Deploy
GCP_PROJECT = os.getenv("GCP_PROJECT", "")
CLOUD_RUN_SERVICE = os.getenv("CLOUD_RUN_SERVICE", "ents-academy")

# Agent / Ops
AGENT_LOG_RETENTION_DAYS = 90  # For contest evidence window

# Pricing (for viability + impact narrative)
FREE_TIER_PHASES = ["00"]  # Limited access
PRO_MONTHLY_PRICE = 29  # USD

def get_gemini_key() -> str:
    if not GEMINI_API_KEY:
        # In real deploy, fail loud or use Vertex ADC
        print("⚠️ WARNING: No GEMINI_API_KEY set. Set for tutor + agents (required for XPRIZE Gemini API rule).")
    return GEMINI_API_KEY
