"""
web/app.py - Ents Academy FastAPI app (the AI-native business for Gemini XPRIZE).

Key for winning:
- Gemini API calls in deployed paths (tutor, agents).
- Google Cloud Run hosting.
- Agent execution logs + decisions visible (AI-Native).
- Stripe revenue tracking.
- Real users/progress for Business Viability + Category Impact (Education).

Run: uvicorn web.app:app --reload
Deploy: docker build + gcloud run deploy (see README + plan.md).
"""

from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os
import datetime
import shutil
import tempfile
from pathlib import Path as PyPath

from .config import APP_NAME, DEBUG, PRO_MONTHLY_PRICE, FREE_TIER_PHASES, get_gemini_key, USE_VERTEX
from .deps import get_db, get_stripe, Base, engine
from . import models
from .oracle import grade_submission
from .agents.scheduler import start_agents, stop_agents
from .system1 import decide, decide_flow, status as system1_status
from .system1.questions import QuestionError
# ensure models registered for queries in /ops
_ = models.User, models.AgentDecision, models.RevenueEvent

# Ensure tables (dev; prod use migrations)
Base.metadata.create_all(bind=engine)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start AI agents on boot -> they run continuously, execute decisions, log (perfect evidence)
    start_agents()
    yield
    stop_agents()

app = FastAPI(title=APP_NAME, debug=DEBUG, lifespan=lifespan)

# Static + templates (Ents forest dark theme via Tailwind play CDN + custom)
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Simple in-mem demo "current user" for fast MVP (replace with real auth later)
DEMO_USER = {"id": 1, "email": "explorer@fangorn.dev", "is_pro": False, "progress": {"00": ["jax", "max"], "01": []}}

@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    gemini_ready = bool(get_gemini_key() or USE_VERTEX)
    return templates.TemplateResponse(request, "landing.html", {
        "app_name": APP_NAME,
        "pro_price": PRO_MONTHLY_PRICE,
        "gemini_ready": gemini_ready,
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db=Depends(get_db)):
    # TODO: real user from session
    user = DEMO_USER
    return templates.TemplateResponse(request, "dashboard.html", {
        "user": user,
        "phases": ["00", "01", "02"],
    })

@app.get("/lab/{phase}/{pillar}", response_class=HTMLResponse)
async def lab(phase: str, pillar: str, request: Request):
    # Stub: later load real SUBJECT + template code from curriculum/
    lore = f"Level {phase} - {pillar.upper()} Pillar. Edit, summon the (AI) Oracle."
    return templates.TemplateResponse(request, "lab.html", {
        "phase": phase,
        "pillar": pillar,
        "lore": lore,
        "template_code": "# Your code here\nprint('Wake the Ent...')",
    })

@app.post("/lab/{phase}/{pillar}/submit")
async def submit_code(phase: str, pillar: str, code: str = Form(...)):
    """Uses real oracle.py (reuses grademe logic + Gemini review). Gemini call here = compliance."""
    result = grade_submission(phase, pillar, code)
    return JSONResponse({"status": "reviewed", **result})

@app.get("/tutor", response_class=HTMLResponse)
async def tutor_page(request: Request):
    return templates.TemplateResponse(request, "tutor.html", {})

@app.post("/tutor/ask")
async def tutor_ask(question: str = Form(...), session_id: str = Form("")):
    """System 1 gate in front of the tutor. High confidence skips the LLM."""
    from .system1.flows import tutor_state
    outcome = decide_flow("tutor", tutor_state(question), session_id=session_id or None)
    return {
        "answer": outcome["text"],
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "system1": _public_system1(outcome),
    }

@app.get("/ops", response_class=HTMLResponse)
async def ops_dashboard(request: Request, db=Depends(get_db)):
    """AI-Native ops visibility - key for judges (agent logs, decisions, Gemini usage)."""
    # Real logs from DB (populated by agents + every Gemini call site)
    decisions = db.query(models.AgentDecision).order_by(models.AgentDecision.ts.desc()).limit(20).all()
    logs = [_ops_log(d) for d in decisions]
    if not logs:
        logs = [{
            "ts": "demo",
            "agent": "RetentionAgent (demo)",
            "decision": "Run /ops/trigger-retention to execute a System 1 gated decision now.",
            "gemini": False,
            "system1": False,
            "action": "",
        }]
    return templates.TemplateResponse(request, "ops.html", {
        "logs": logs,
        "gemini_calls_today": sum(1 for row in logs if row.get("gemini")),
        "system1_decisions": sum(1 for row in logs if row.get("system1")),
    })

@app.post("/ops/trigger-retention")
async def trigger_retention():
    from .agents.retention import run_retention_agent
    run_retention_agent(dry_run=False)
    return {"triggered": "retention", "note": "Check /ops for the System 1 decision and the retention action."}

@app.post("/ops/trigger-content")
async def trigger_content():
    from .agents.content import run_content_agent
    run_content_agent(dry_run=False)
    return {"triggered": "content"}

@app.get("/download/{phase}")
async def download_workspace(phase: str):
    """Download clean student workspace for local Oracle (grademe.sh + pixi). This + web tutor = hybrid strength."""
    base = PyPath(__file__).parent.parent / "max_env" / "phases"
    phase_map = {
        "00": "C00_The_Seed",
        "01": "C01_The_Enting",
        "02": "C02_The_Lexicon",
    }
    pdir = base / phase_map.get(phase, "C00_The_Seed")
    if not pdir.exists():
        raise HTTPException(404, "Phase not ready")
    # Zip the ex* + grademe + SUBJECT (students edit copies)
    tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    tmp.close()
    shutil.make_archive(tmp.name[:-4], "zip", root_dir=str(pdir.parent), base_dir=pdir.name)
    zip_path = tmp.name[:-4] + ".zip"
    return FileResponse(zip_path, filename=f"ents_phase{phase}_workspace.zip", media_type="application/zip")


@app.get("/pricing", response_class=HTMLResponse)
async def pricing(request: Request):
    return templates.TemplateResponse(request, "pricing.html", { "price": PRO_MONTHLY_PRICE})

# --- Stripe (revenue evidence) ---
@app.post("/stripe/checkout")
async def create_checkout():
    stripe = get_stripe()
    # In real: create session for logged in user, return url
    # For MVP stub: return test link
    return {"url": "https://checkout.stripe.com/test (configure real in prod for XPRIZE revenue proof)", "note": "After checkout, webhook credits Pro + logs RevenueEvent."}

@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    # TODO: verify sig with STRIPE_WEBHOOK_SECRET, handle checkout.session.completed -> activate Pro, insert RevenueEvent
    payload = await request.body()
    print(f"[STRIPE_WEBHOOK] Received (len={len(payload)}). In prod: parse + credit user + record for monthly export.")
    return {"status": "ok (stub)"}

# Health for Cloud Run
@app.get("/system1/status")
async def system1_status_route():
    """Which System 1 backend would run, without loading weights."""
    return system1_status()


@app.post("/system1/decide")
async def system1_decide(request: Request):
    """Score a state. Pass ``flow`` (tutor|retention) or explicit ``questions``."""
    try:
        body = await request.json()
    except Exception as exc:
        raise HTTPException(400, f"expected JSON body ({exc})") from exc
    if not isinstance(body, dict):
        raise HTTPException(400, "expected a JSON object")
    state = body.get("state")
    if state is None:
        raise HTTPException(400, "state is required")
    flow = body.get("flow")
    questions = body.get("questions")
    raw_session = body.get("session_id")
    session_id = raw_session.strip() if isinstance(raw_session, str) and raw_session.strip() else None
    try:
        if questions is None:
            if not flow:
                raise QuestionError("pass flow (tutor|retention) or questions")
            outcome = decide_flow(str(flow), state, session_id=session_id)
        else:
            outcome = decide(
                state,
                questions,
                flow=str(flow or "raw"),
                session_id=session_id,
            )
    except QuestionError as exc:
        raise HTTPException(400, str(exc)) from exc
    return _public_system1(outcome, include_text=True)


@app.get("/healthz")
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": APP_NAME,
        "gemini_configured": bool(get_gemini_key() or USE_VERTEX),
        "system1": system1_status(),
    }

@app.get("/judges", response_class=HTMLResponse)
async def judges_page(request: Request):
    """Dedicated page for XPRIZE judges and reviewers."""
    return templates.TemplateResponse(request, "judges.html", {
        "app_name": APP_NAME,
    })

def _public_system1(outcome: dict, include_text: bool = False) -> dict:
    payload = {
        "route": outcome["route"],
        "reason": outcome["reason"],
        "backend": outcome["backend"],
        "requested_backend": outcome["requested_backend"],
        "fallback_reason": outcome["fallback_reason"],
        "model": outcome.get("model"),
        "confidence": outcome["confidence"],
        "answers": outcome["answers"],
        "generative_provider": outcome["generative_provider"],
        "flow": outcome["flow"],
        "system2_model": outcome.get("system2_model"),
        "cost_tier": outcome.get("cost_tier"),
        "session_id": outcome.get("session_id"),
        "draft_model": outcome.get("draft_model"),
    }
    if include_text:
        payload["text"] = outcome["text"]
    return payload


def _ops_log(row) -> dict:
    name = row.agent_name or ""
    action = row.action_taken or ""
    system1 = name.startswith("System1") or action.startswith("system1:")
    # ContentAgent still calls Gemini directly. System 1 rows badge GEMINI
    # only when that gate actually drafted with Gemini.
    live_gemini = name == "ContentAgent" or action.startswith("system1:generative:gemini")
    return {
        "ts": str(row.ts),
        "agent": name,
        "decision": row.decision,
        "gemini": live_gemini,
        "system1": system1,
        "action": action,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
