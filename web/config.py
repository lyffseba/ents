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


# --- System 1 decision bus (web/system1) ---
# Empty SYSTEM1_BACKEND prefers local Laya, then the mock heuristic if weights
# or the package are missing. OPENROUTER_API_KEY serves Jev (System 1) and
# chat drafts (System 2). Without that key, Jev falls back to the mock and
# escalations skip OpenRouter. Demo mode leaves both keys empty.
# See README "System 1 decision bus".

def system1_backend_setting() -> str:
    """``laya``, ``openrouter_jev``, ``mock``, or ``""`` (prefer local Laya)."""
    return os.getenv("SYSTEM1_BACKEND", "").strip().lower()


def openrouter_api_key() -> str:
    return os.getenv("OPENROUTER_API_KEY", "").strip()


def system1_high_confidence() -> float:
    raw = os.getenv("SYSTEM1_HIGH_CONFIDENCE", "0.85")
    try:
        value = float(raw)
    except ValueError:
        return 0.85
    if not 0.0 <= value <= 1.0:
        return 0.85
    return value


def system1_needs_generation_threshold() -> float:
    """Noul at or above this on ``needs_generation`` always drafts with System 2."""
    raw = os.getenv("SYSTEM1_NEEDS_GENERATION", "0.5")
    try:
        value = float(raw)
    except ValueError:
        return 0.5
    if not 0.0 <= value <= 1.0:
        return 0.5
    return value


# Pinned against OpenRouter docs (2026-09-25):
# https://openrouter.ai/docs/guides/routing/routers/auto-router
# https://openrouter.ai/docs/guides/routing/routers/free-router
# Auto is the System 2 default. It bills the selected model's rate and adds
# no surcharge. Free is the zero-cost override. Neither id is a Jev model.
SYSTEM2_FREE_MODEL = "openrouter/free"
SYSTEM2_AUTO_MODEL = "openrouter/auto"
_SYSTEM1_JEV_DEFAULT = "typesafe/jev-1.13"
_CHAT_ROUTER_IDS = {SYSTEM2_FREE_MODEL, SYSTEM2_AUTO_MODEL, "openrouter/auto-beta"}


def system1_jev_model() -> str:
    """Typed-decision model. Chat routers are rejected so Auto never scores System 1."""
    raw = os.getenv("SYSTEM1_JEV_MODEL", "").strip() or _SYSTEM1_JEV_DEFAULT
    if raw in _CHAT_ROUTER_IDS or raw.endswith(":free"):
        print(f"[SYSTEM1] SYSTEM1_JEV_MODEL={raw!r} is a chat model; using {_SYSTEM1_JEV_DEFAULT}")
        return _SYSTEM1_JEV_DEFAULT
    return raw


def system2_model_allowed(model: str) -> bool:
    """System 2 may call Auto, the free router, or a ``:free`` model. Not a fixed paid id."""
    if model in {SYSTEM2_FREE_MODEL, SYSTEM2_AUTO_MODEL}:
        return True
    return model.endswith(":free") and not model.startswith(":")


def system2_model() -> str:
    """Chat model for escalations. Default ``openrouter/auto``.

    ``SYSTEM2_MODEL=openrouter/free`` is the zero-cost lane. A ``:free`` id is
    also sent as-is. Any other value is ignored and ``openrouter/auto`` is used.
    Jev stays on ``system1_jev_model()``.
    """
    raw = os.getenv("SYSTEM2_MODEL", "").strip()
    if not raw:
        return SYSTEM2_AUTO_MODEL
    if system2_model_allowed(raw):
        return raw
    print(
        f"[SYSTEM1] SYSTEM2_MODEL={raw!r} is not {SYSTEM2_AUTO_MODEL}, "
        f"{SYSTEM2_FREE_MODEL}, or a :free model; using {SYSTEM2_AUTO_MODEL}"
    )
    return SYSTEM2_AUTO_MODEL


def system2_cost_tier_override() -> str | None:
    """Explicit Auto ``cost_tier``, or None so the gate maps urgency/confidence."""
    raw = os.getenv("SYSTEM2_COST_TIER", "").strip().lower()
    if not raw:
        return None
    if raw in {"low", "medium", "high", "xhigh", "max"}:
        return raw
    print(f"[SYSTEM1] SYSTEM2_COST_TIER={raw!r} is not a cost tier; mapping from System 1")
    return None


def openrouter_decisions_url() -> str:
    return os.getenv(
        "OPENROUTER_DECISIONS_URL",
        "https://openrouter.ai/api/alpha/decisions",
    ).strip()


def openrouter_chat_url() -> str:
    return os.getenv(
        "OPENROUTER_CHAT_URL",
        "https://openrouter.ai/api/v1/chat/completions",
    ).strip()


# Public bundle. English weights live at the repo root; multilingual and
# typed-decisions are subfolders. Laya is not gated; HF_TOKEN is optional.
LAYA_BUNDLE_REPO = "convaiinnovations/laya"


def system1_laya_model() -> str:
    """Checkpoint name. Empty lets ``Router`` choose english vs multilingual.

    Accepted at predict time: ``english``, ``multilingual``, ``typed-decisions``,
    and the aliases Laya documents (``en``, ``multi``, ``typed``, …).
    """
    return os.getenv("SYSTEM1_LAYA_MODEL", "").strip()


def system1_laya_device() -> str:
    """``cpu``, ``cuda``, or ``mps``. Empty lets Laya pick."""
    return os.getenv("SYSTEM1_LAYA_DEVICE", "").strip()


def system1_laya_preload() -> bool:
    return os.getenv("SYSTEM1_LAYA_PRELOAD", "").lower() in {"1", "true", "yes"}


def system1_laya_path() -> str:
    """Local checkpoint directory. When set, that checkpoint is not downloaded."""
    return os.getenv("SYSTEM1_LAYA_PATH", "").strip()


def system1_laya_repo() -> str:
    """Hub repo or standalone checkpoint repo. Default is the public bundle."""
    return os.getenv("SYSTEM1_LAYA_REPO", "").strip() or LAYA_BUNDLE_REPO


def system1_laya_revision() -> str:
    """Optional Hub revision (commit, branch, or tag) applied to every load."""
    return os.getenv("SYSTEM1_LAYA_REVISION", "").strip()


def system1_laya_token() -> str:
    """Optional Hugging Face token. ``SYSTEM1_LAYA_TOKEN`` wins over ``HF_TOKEN``."""
    return os.getenv("SYSTEM1_LAYA_TOKEN", "").strip() or os.getenv("HF_TOKEN", "").strip()


def system1_laya_max_len() -> int | None:
    """Optional ``Router.predict(max_len=...)``. Unset or invalid means Laya's default."""
    raw = os.getenv("SYSTEM1_LAYA_MAX_LEN", "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        return None
    if value < 1:
        return None
    return value


def system1_laya_max_loaded() -> int | None:
    """How many checkpoints stay resident. Unset keeps Laya's default (2)."""
    raw = os.getenv("SYSTEM1_LAYA_MAX_LOADED", "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        return None
    if value < 1:
        return None
    return value


def system1_laya_auto_task() -> bool:
    """Opt in to automatic ``typed-decisions`` routing. Off unless set."""
    return os.getenv("SYSTEM1_LAYA_AUTO_TASK", "").strip().lower() in {"1", "true", "yes"}
