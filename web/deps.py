"""
web/deps.py - Shared dependencies (DB, clients) for Ents Academy FastAPI app.
Initialized on startup. For XPRIZE: ensure Gemini + Stripe ready for prod evidence.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL, STRIPE_SECRET_KEY, get_gemini_key, USE_VERTEX

# SQLAlchemy setup (sqlite dev; easy to swap to postgres for Cloud SQL)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI dependency for DB sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Stripe client (lazy; real revenue proof via webhooks + exports)
import stripe
stripe.api_key = STRIPE_SECRET_KEY

def get_stripe():
    return stripe

# Gemini client (core of AI-native + mandatory LLM call in deployed app)
# Prefer google-generativeai for speed; switch to vertexai for pure Google Cloud.
_gemini_model = None

def get_gemini_model():
    """Return configured model or None when no credentials (demo mode)."""
    global _gemini_model
    if _gemini_model is not None:
        return _gemini_model

    api_key = get_gemini_key()
    if USE_VERTEX:
        try:
            from vertexai.generative_models import GenerativeModel
            from .config import GEMINI_MODEL
            _gemini_model = GenerativeModel(GEMINI_MODEL)
            print("✅ Gemini via Vertex AI (Google Cloud)")
            return _gemini_model
        except Exception as e:
            print(f"Vertex init failed ({e}), falling back to google-generativeai")

    if not api_key:
        print("⚠️ GEMINI_API_KEY unset — demo mode (deterministic mock responses).")
        return None

    import google.generativeai as genai
    from .config import GEMINI_MODEL
    genai.configure(api_key=api_key)
    _gemini_model = genai.GenerativeModel(model_name=GEMINI_MODEL)
    print("✅ Gemini via google-generativeai")
    return _gemini_model


def call_gemini(prompt: str, system: str = "") -> str:
    """Central wrapper: ALWAYS log for contest evidence. Demo-safe without keys."""
    import datetime
    model = get_gemini_model()
    try:
        if model is None:
            text = (
                f"[demo-gemini] Treebeard acknowledges: {prompt[:120]}… "
                "Set GEMINI_API_KEY for live XPRIZE evidence."
            )
        elif USE_VERTEX:
            resp = model.generate_content(prompt)
            text = resp.text if hasattr(resp, "text") else str(resp)
        else:
            if system:
                resp = model.generate_content([system, prompt])
            else:
                resp = model.generate_content(prompt)
            text = resp.text
    except Exception as e:
        text = f"[Gemini error: {e}]"

    print(
        f"[GEMINI_LOG] {datetime.datetime.utcnow().isoformat()} | "
        f"prompt[:80]={prompt[:80]!r} | out[:80]={text[:80]!r}"
    )
    return text
