#!/usr/bin/env python3
"""System 1 decision bus tests.

Demo/mock mode: no Gemini key and no OpenRouter key. Covers the mock
backend, confidence gating, and the tutor plus retention flows.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

_DB = tempfile.NamedTemporaryFile(prefix="ents-system1-", suffix=".db", delete=False)
_DB.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_DB.name}"
os.environ["ENTS_DISABLE_SCHEDULER"] = "1"
os.environ["GEMINI_API_KEY"] = ""
os.environ["USE_VERTEX"] = "false"
os.environ["OPENROUTER_API_KEY"] = ""
os.environ["SYSTEM1_BACKEND"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402
from web.app import app  # noqa: E402
from web import deps  # noqa: E402
from web.agents import content as content_agent  # noqa: E402
from web.config import system1_jev_model, system2_model  # noqa: E402
from web.system1.backends import laya_importable, predict, reset_backend_state  # noqa: E402
from web.system1.flows import tutor_state  # noqa: E402
from web.system1.gate import auto_cost_tier, classify_route  # noqa: E402
from web.system1.bus import session_id_from_state  # noqa: E402
from web.system1.questions import normalize_questions  # noqa: E402
from web.deps import SessionLocal  # noqa: E402
from web.models import AgentDecision  # noqa: E402
from web.system1 import decide_flow  # noqa: E402

_GEMINI_CALLS = {"n": 0}
_REAL_GEMINI = deps.call_gemini


def _counting_gemini(prompt: str, system: str = "") -> str:
    _GEMINI_CALLS["n"] += 1
    return _REAL_GEMINI(prompt, system)


deps.call_gemini = _counting_gemini
content_agent.call_gemini = _counting_gemini

_CLIENT = TestClient(app)

_BILLING = {
    "department": {
        "type": "choice",
        "instructions": "Which department should handle this?",
        "criteria": {
            "billing": "invoices payments refunds",
            "technical": "bugs outages crashes",
        },
    },
    "urgency": {
        "type": "score",
        "instructions": "How urgent is this request?",
        "criteria": ["not urgent", "soon", "critical deadline or blocking issue"],
    },
    "needs_generation": {
        "type": "noul",
        "instructions": "Does this case need a personalized written message instead of a fixed template?",
    },
}


class _EnvGuard(unittest.TestCase):
    def setUp(self):
        reset_backend_state()
        self._saved = {
            key: os.environ.get(key)
            for key in (
                "SYSTEM1_BACKEND",
                "OPENROUTER_API_KEY",
                "SYSTEM1_HIGH_CONFIDENCE",
                "SYSTEM1_NEEDS_GENERATION",
                "SYSTEM1_JEV_MODEL",
                "SYSTEM2_MODEL",
                "SYSTEM2_COST_TIER",
                "OPENROUTER_DECISIONS_URL",
                "OPENROUTER_CHAT_URL",
            )
        }
        os.environ["SYSTEM1_BACKEND"] = "mock"
        os.environ["OPENROUTER_API_KEY"] = ""
        os.environ.pop("SYSTEM1_HIGH_CONFIDENCE", None)
        os.environ.pop("SYSTEM1_NEEDS_GENERATION", None)
        os.environ.pop("SYSTEM1_JEV_MODEL", None)
        os.environ.pop("SYSTEM2_MODEL", None)
        os.environ.pop("SYSTEM2_COST_TIER", None)
        os.environ.pop("OPENROUTER_DECISIONS_URL", None)
        os.environ.pop("OPENROUTER_CHAT_URL", None)

    def tearDown(self):
        reset_backend_state()
        for key, value in self._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


class MockBackendTests(_EnvGuard):
    def test_mock_returns_choice_score_and_noul(self):
        result = predict("Please refund the duplicate invoice payment", _BILLING)
        self.assertEqual(result["backend"], "mock")
        self.assertEqual(result["requested_backend"], "mock")
        self.assertIsNone(result["fallback_reason"])
        department = result["answers"]["department"]
        self.assertEqual(department["choice"], "billing")
        self.assertGreaterEqual(department["confidence"], 0.85)
        self.assertIsInstance(result["answers"]["urgency"]["score"], float)
        self.assertIsInstance(result["answers"]["needs_generation"]["noul"], float)

    def test_choice_score_noul_spellings_normalize(self):
        normalized = normalize_questions({
            "keep": {"type": "Choice", "instructions": "Which?", "criteria": {"a": "one", "b": "two"}},
            "rank": {"type": "Score", "instructions": "How much?", "criteria": ["low", "high"]},
            "flag": {"type": "Noul", "instructions": "Is it true?"},
        })
        self.assertEqual(normalized["keep"]["type"], "choice")
        self.assertEqual(normalized["rank"]["type"], "score")
        self.assertEqual(normalized["flag"]["type"], "noul")

    def test_openrouter_jev_without_key_uses_mock(self):
        os.environ["SYSTEM1_BACKEND"] = "openrouter_jev"
        os.environ["OPENROUTER_API_KEY"] = ""
        result = predict("Please refund the duplicate invoice payment", {
            "department": _BILLING["department"],
        })
        self.assertEqual(result["requested_backend"], "openrouter_jev")
        self.assertEqual(result["backend"], "mock")
        self.assertIn("OPENROUTER_API_KEY", result["fallback_reason"])

    def test_missing_laya_package_uses_mock(self):
        if laya_importable():
            self.skipTest("laya is installed; missing-package fallback is not the path under test")
        os.environ["SYSTEM1_BACKEND"] = "laya"
        result = predict("What is softmax?", {
            "intent": {
                "type": "choice",
                "instructions": "What kind of help?",
                "criteria": {"define": "softmax embedding", "open": "generated explanation"},
            },
        })
        self.assertEqual(result["requested_backend"], "laya")
        self.assertEqual(result["backend"], "mock")
        self.assertIn("laya", result["fallback_reason"].lower())


class ConfidenceGateTests(_EnvGuard):
    def test_high_confidence_is_deterministic(self):
        route, reason, confidence = classify_route({
            "intent": {"choice": "define", "confidence": 0.99},
            "needs_generation": {"noul": 0.04, "confidence": 0.92},
            "difficulty": {"score": 0.2, "confidence": 0.1},
        })
        self.assertEqual(route, "deterministic")
        self.assertEqual(reason, "high_confidence")
        self.assertGreaterEqual(confidence, 0.85)

    def test_low_confidence_is_generative(self):
        route, reason, confidence = classify_route({
            "intent": {"choice": "define", "confidence": 0.25},
        })
        self.assertEqual(route, "generative")
        self.assertEqual(reason, "mid_or_low_confidence")
        self.assertLess(confidence, 0.85)

    def test_needs_generation_overrides_a_confident_choice(self):
        route, reason, _confidence = classify_route({
            "intent": {"choice": "define", "confidence": 0.99},
            "needs_generation": {"noul": 0.86, "confidence": 0.72},
        })
        self.assertEqual(route, "generative")
        self.assertEqual(reason, "needs_generation")

    def test_threshold_is_read_from_the_environment(self):
        os.environ["SYSTEM1_HIGH_CONFIDENCE"] = "0.99"
        route, reason, _confidence = classify_route({
            "intent": {"choice": "define", "confidence": 0.92},
        })
        self.assertEqual(route, "generative")
        self.assertEqual(reason, "mid_or_low_confidence")


class GatedFlowTests(_EnvGuard):
    def test_tutor_glossary_skips_the_generative_call(self):
        before = _GEMINI_CALLS["n"]
        outcome = decide_flow("tutor", tutor_state("What is softmax?"))
        self.assertEqual(outcome["route"], "deterministic")
        self.assertEqual(outcome["backend"], "mock")
        self.assertIsNone(outcome["generative_provider"])
        self.assertIn("softmax", outcome["text"].lower())
        self.assertNotIn("[demo-gemini]", outcome["text"])
        self.assertEqual(_GEMINI_CALLS["n"], before)

        response = _CLIENT.post("/tutor/ask", data={"question": "What is softmax?"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["system1"]["route"], "deterministic")
        self.assertEqual(_GEMINI_CALLS["n"], before)

    def test_ambiguous_tutor_question_uses_demo_draft_without_keys(self):
        self.assertFalse(os.environ.get("OPENROUTER_API_KEY"))
        self.assertFalse(os.environ.get("GEMINI_API_KEY"))
        before = _GEMINI_CALLS["n"]
        response = _CLIENT.post("/tutor/ask", data={"question": "???"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["system1"]["route"], "generative")
        self.assertEqual(body["system1"]["generative_provider"], "demo")
        self.assertTrue(body["answer"].startswith("[demo-gemini]"))
        self.assertEqual(_GEMINI_CALLS["n"], before + 1)

    def test_retention_trigger_logs_a_deterministic_system1_decision(self):
        before = _GEMINI_CALLS["n"]
        triggered = _CLIENT.post("/ops/trigger-retention")
        self.assertEqual(triggered.status_code, 200)
        self.assertEqual(_GEMINI_CALLS["n"], before)

        ops = _CLIENT.get("/ops")
        self.assertEqual(ops.status_code, 200)
        page = ops.text
        self.assertIn("SYSTEM 1", page)
        self.assertIn("flow=retention", page)
        self.assertIn("route=deterministic", page)
        self.assertIn("intervention=nudge", page)


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = json.dumps(payload)

    def raise_for_status(self):
        if self.status_code >= 400:
            import httpx
            request = httpx.Request("POST", "https://openrouter.ai/mock")
            response = httpx.Response(self.status_code, request=request, text=self.text)
            raise httpx.HTTPStatusError("error", request=request, response=response)

    def json(self):
        return self._payload


def _jev_payload():
    """Shape captured from the OpenRouter Jev tutorial (typesafe/jev-1.13)."""
    return {
        "id": "gen-dec-test",
        "model": "typesafe/jev-1.13-20260917",
        "provider": "TypeSafe",
        "answers": {
            "department": {
                "type": "choice",
                "choice": "billing",
                "confidence": 0.91,
                "probabilities": {"billing": 0.94, "technical": 0.06},
            },
            "urgency": {
                "type": "score",
                "score": 1.4,
                "confidence": 0.8,
                "probabilities": {"0": 0.1, "1": 0.4, "2": 0.5},
            },
            "needs_generation": {"type": "noul", "noul": 0.12},
        },
        "usage": {"input_tokens": 120, "output_tokens": 40, "cost": 0.00001},
    }


def _chat_payload(text="A drafted hint about shapes."):
    return {
        "id": "gen-chat-test",
        "model": "some-vendor/model:free",
        "choices": [{"message": {"role": "assistant", "content": text}}],
    }


class OpenRouterBackendTests(_EnvGuard):
    def test_default_models_pin_jev_and_the_auto_router(self):
        self.assertEqual(system1_jev_model(), "typesafe/jev-1.13")
        self.assertEqual(system2_model(), "openrouter/auto")

    def test_system2_allows_auto_free_router_and_free_suffix_only(self):
        os.environ["SYSTEM2_MODEL"] = "openrouter/free"
        self.assertEqual(system2_model(), "openrouter/free")
        os.environ["SYSTEM2_MODEL"] = "meta-llama/llama-3.2-3b-instruct:free"
        self.assertEqual(system2_model(), "meta-llama/llama-3.2-3b-instruct:free")
        os.environ["SYSTEM2_MODEL"] = "openai/gpt-4o-mini"
        self.assertEqual(system2_model(), "openrouter/auto")
        os.environ["SYSTEM2_MODEL"] = "openrouter/auto-beta"
        self.assertEqual(system2_model(), "openrouter/auto")

    def test_jev_model_rejects_chat_routers(self):
        os.environ["SYSTEM1_JEV_MODEL"] = "openrouter/auto"
        self.assertEqual(system1_jev_model(), "typesafe/jev-1.13")
        os.environ["SYSTEM1_JEV_MODEL"] = "openrouter/free"
        self.assertEqual(system1_jev_model(), "typesafe/jev-1.13")

    def test_jev_posts_decisions_and_normalizes_typed_answers(self):
        os.environ["SYSTEM1_BACKEND"] = "openrouter_jev"
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test"
        captured = {}

        def fake_post(url, headers=None, json=None, timeout=None):
            captured["url"] = url
            captured["headers"] = headers
            captured["json"] = json
            captured["timeout"] = timeout
            return _FakeResponse(_jev_payload())

        with patch("httpx.post", side_effect=fake_post) as mocked:
            result = predict("Please refund the duplicate invoice payment", _BILLING)

        self.assertEqual(mocked.call_count, 1)
        self.assertEqual(captured["url"], "https://openrouter.ai/api/alpha/decisions")
        self.assertEqual(captured["headers"]["Authorization"], "Bearer sk-or-test")
        self.assertEqual(captured["json"]["model"], "typesafe/jev-1.13")
        self.assertNotIn("plugins", captured["json"])
        self.assertNotIn("session_id", captured["json"])
        self.assertNotEqual(captured["json"]["model"], "openrouter/auto")
        self.assertEqual(captured["json"]["state"], "Please refund the duplicate invoice payment")
        self.assertEqual(captured["json"]["questions"]["department"]["type"], "choice")
        self.assertEqual(result["backend"], "openrouter_jev")
        self.assertEqual(result["requested_backend"], "openrouter_jev")
        self.assertIsNone(result["fallback_reason"])
        self.assertEqual(result["model"], "typesafe/jev-1.13-20260917")
        self.assertEqual(result["answers"]["department"]["choice"], "billing")
        self.assertEqual(result["answers"]["urgency"]["score"], 1.4)
        self.assertAlmostEqual(result["answers"]["needs_generation"]["noul"], 0.12)
        # Jev noul answers omit confidence; the bus derives |2p-1|.
        self.assertAlmostEqual(result["answers"]["needs_generation"]["confidence"], round(abs(0.12 - 0.5) * 2, 4))

    def test_jev_http_error_falls_back_to_mock_without_raising(self):
        os.environ["SYSTEM1_BACKEND"] = "openrouter_jev"
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test"

        def fake_post(url, headers=None, json=None, timeout=None):
            return _FakeResponse({"error": "upstream"}, status_code=503)

        with patch("httpx.post", side_effect=fake_post):
            result = predict("Please refund the duplicate invoice payment", {
                "department": _BILLING["department"],
            })
        self.assertEqual(result["backend"], "mock")
        self.assertEqual(result["requested_backend"], "openrouter_jev")
        self.assertIn("openrouter jev", result["fallback_reason"])
        self.assertEqual(result["answers"]["department"]["choice"], "billing")

    def test_jev_missing_answers_falls_back_to_mock(self):
        os.environ["SYSTEM1_BACKEND"] = "openrouter_jev"
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test"

        def fake_post(url, headers=None, json=None, timeout=None):
            return _FakeResponse({"model": "typesafe/jev-1.13", "answers": {}})

        with patch("httpx.post", side_effect=fake_post):
            result = predict("Please refund the duplicate invoice payment", {
                "department": _BILLING["department"],
            })
        self.assertEqual(result["backend"], "mock")
        self.assertIn("missing answers", result["fallback_reason"])

    def test_no_key_skips_openrouter_http_and_uses_demo_draft(self):
        self.assertEqual(os.environ.get("OPENROUTER_API_KEY"), "")
        before = _GEMINI_CALLS["n"]
        with patch("httpx.post", side_effect=AssertionError("unexpected network")) as mocked:
            response = _CLIENT.post("/tutor/ask", data={"question": "???"})
        self.assertEqual(mocked.call_count, 0)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["system1"]["route"], "generative")
        self.assertEqual(body["system1"]["generative_provider"], "demo")
        self.assertTrue(body["answer"].startswith("[demo-gemini]"))
        self.assertEqual(_GEMINI_CALLS["n"], before + 1)

    def test_escalated_tutor_drafts_with_the_free_chat_model(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test"
        before = _GEMINI_CALLS["n"]
        captured = {}

        def fake_post(url, headers=None, json=None, timeout=None):
            captured["url"] = url
            captured["headers"] = headers
            captured["json"] = json
            return _FakeResponse(_chat_payload())

        with patch("httpx.post", side_effect=fake_post) as mocked:
            response = _CLIENT.post("/tutor/ask", data={"question": "???"})

        self.assertEqual(mocked.call_count, 1)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["system1"]["route"], "generative")
        self.assertEqual(body["system1"]["reason"], "needs_generation")
        self.assertEqual(body["system1"]["generative_provider"], "openrouter")
        self.assertEqual(body["answer"], "A drafted hint about shapes.")
        self.assertEqual(captured["url"], "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(captured["json"]["model"], "openrouter/auto")
        plugin = captured["json"]["plugins"][0]
        self.assertEqual(plugin["id"], "auto-router")
        self.assertIn(plugin["cost_tier"], ("low", "medium", "high", "xhigh", "max"))
        self.assertNotIn("session_id", captured["json"])
        self.assertEqual(captured["headers"]["Authorization"], "Bearer sk-or-test")
        self.assertEqual(
            [message["role"] for message in captured["json"]["messages"]],
            ["system", "user"],
        )
        self.assertIn("???", captured["json"]["messages"][1]["content"])
        self.assertEqual(_GEMINI_CALLS["n"], before)

    def test_system2_model_override_is_sent_to_chat(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test"
        os.environ["SYSTEM2_MODEL"] = "meta-llama/llama-3.2-3b-instruct:free"
        captured = {}

        def fake_post(url, headers=None, json=None, timeout=None):
            captured["model"] = json["model"]
            return _FakeResponse(_chat_payload("Pinned free draft."))

        with patch("httpx.post", side_effect=fake_post):
            outcome = decide_flow("tutor", tutor_state("???"))
        self.assertEqual(captured["model"], "meta-llama/llama-3.2-3b-instruct:free")
        self.assertEqual(outcome["generative_provider"], "openrouter")
        self.assertEqual(outcome["text"], "Pinned free draft.")

    def test_auto_router_override_is_sent_to_chat(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test"
        os.environ["SYSTEM2_MODEL"] = "openrouter/auto"
        captured = {}

        def fake_post(url, headers=None, json=None, timeout=None):
            captured["model"] = json["model"]
            return _FakeResponse(_chat_payload("Auto-routed draft."))

        with patch("httpx.post", side_effect=fake_post):
            outcome = decide_flow("tutor", tutor_state("???"))
        self.assertEqual(captured["model"], "openrouter/auto")
        self.assertEqual(outcome["generative_provider"], "openrouter")
        self.assertEqual(outcome["text"], "Auto-routed draft.")

    def test_paid_system2_model_is_not_sent(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test"
        os.environ["SYSTEM2_MODEL"] = "openai/gpt-4o-mini"
        captured = {}

        def fake_post(url, headers=None, json=None, timeout=None):
            captured["model"] = json["model"]
            return _FakeResponse(_chat_payload("Free draft."))

        with patch("httpx.post", side_effect=fake_post):
            outcome = decide_flow("tutor", tutor_state("???"))
        self.assertEqual(captured["model"], "openrouter/auto")
        self.assertEqual(outcome["text"], "Free draft.")
        self.assertNotIn("gpt-4o-mini", captured["model"])

    def test_chat_http_error_falls_back_to_demo_draft(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test"
        before = _GEMINI_CALLS["n"]

        def fake_post(url, headers=None, json=None, timeout=None):
            return _FakeResponse({"error": "rate limit"}, status_code=429)

        with patch("httpx.post", side_effect=fake_post):
            outcome = decide_flow("tutor", tutor_state("???"))
        self.assertEqual(outcome["route"], "generative")
        self.assertEqual(outcome["generative_provider"], "demo")
        self.assertTrue(outcome["text"].startswith("[demo-gemini]"))
        self.assertEqual(_GEMINI_CALLS["n"], before + 1)

    def test_retention_escalation_drafts_on_openrouter(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test"
        before = _GEMINI_CALLS["n"]
        captured = {}

        def fake_post(url, headers=None, json=None, timeout=None):
            captured["url"] = url
            captured["json"] = json
            return _FakeResponse(_chat_payload("Come back to the trial. Check the softmax axis."))

        with patch("httpx.post", side_effect=fake_post):
            outcome = decide_flow("retention", {"text": "hmm"})
        self.assertEqual(outcome["flow"], "retention")
        self.assertEqual(outcome["route"], "generative")
        self.assertEqual(outcome["generative_provider"], "openrouter")
        self.assertEqual(outcome["text"], "Come back to the trial. Check the softmax axis.")
        self.assertIn("/chat/completions", captured["url"])
        self.assertEqual(captured["json"]["model"], "openrouter/auto")
        self.assertEqual(captured["json"]["plugins"][0]["id"], "auto-router")
        self.assertIn("Retention", captured["json"]["messages"][0]["content"])
        self.assertEqual(_GEMINI_CALLS["n"], before)

    def test_low_confidence_jev_escalates_to_chat_and_high_confidence_does_not(self):
        os.environ["SYSTEM1_BACKEND"] = "openrouter_jev"
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test"
        calls = []

        def answers(confidence, noul):
            return {
                "model": "typesafe/jev-1.13-20260917",
                "answers": {
                    "intent": {
                        "type": "choice",
                        "choice": "define",
                        "confidence": confidence,
                        "probabilities": {"define": confidence, "hint": 0.0, "lore": 0.0, "open": round(1 - confidence, 4)},
                    },
                    "difficulty": {
                        "type": "score",
                        "score": 0.2,
                        "confidence": 0.9,
                        "probabilities": {"0": 0.8, "1": 0.2, "2": 0.0},
                    },
                    "needs_generation": {"type": "noul", "noul": noul},
                },
            }

        def fake_post(url, headers=None, json=None, timeout=None):
            calls.append(url)
            if "decisions" in url:
                # First call is the low-confidence tutor pass; second is high-confidence.
                noul = 0.9 if len(calls) == 1 else 0.04
                confidence = 0.2 if len(calls) == 1 else 0.99
                return _FakeResponse(answers(confidence, noul))
            return _FakeResponse(_chat_payload("Generated tutor draft."))

        with patch("httpx.post", side_effect=fake_post):
            low = decide_flow("tutor", tutor_state("Explain this in a new way"))
            high = decide_flow("tutor", tutor_state("What is softmax?"))

        self.assertEqual(low["backend"], "openrouter_jev")
        self.assertEqual(low["route"], "generative")
        self.assertEqual(low["reason"], "needs_generation")
        self.assertEqual(low["generative_provider"], "openrouter")
        self.assertEqual(low["text"], "Generated tutor draft.")
        self.assertEqual(high["route"], "deterministic")
        self.assertIsNone(high["generative_provider"])
        self.assertIn("softmax", high["text"].lower())
        self.assertEqual(sum(1 for url in calls if "decisions" in url), 2)
        self.assertEqual(sum(1 for url in calls if "chat/completions" in url), 1)

    def test_auto_draft_maps_urgency_to_cost_tier_and_passes_session_id(self):
        os.environ["SYSTEM1_BACKEND"] = "openrouter_jev"
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test"
        calls = []

        def fake_post(url, headers=None, json=None, timeout=None):
            calls.append((url, json))
            if "decisions" in url:
                return _FakeResponse({
                    "model": "typesafe/jev-1.13-20260917",
                    "answers": {
                        "intervention": {
                            "type": "choice",
                            "choice": "nudge",
                            "confidence": 0.4,
                            "probabilities": {"nudge": 0.4, "discount": 0.2, "tutor_handoff": 0.2, "wait": 0.2},
                        },
                        "urgency": {
                            "type": "score",
                            "score": 2.0,
                            "confidence": 0.99,
                            "probabilities": {"0": 0.0, "1": 0.0, "2": 1.0},
                        },
                        "churn_risk": {"type": "noul", "noul": 0.2},
                        "needs_generation": {"type": "noul", "noul": 0.9},
                    },
                })
            return _FakeResponse({
                "model": "anthropic/claude-sonnet-4.5",
                "choices": [{"message": {"role": "assistant", "content": "Come back this week."}}],
            })

        state = {
            "id": 42,
            "email": "slow@ent.dev",
            "phase": "01",
            "text": "cancel tomorrow",
            "session_id": "learner-42",
        }
        with patch("httpx.post", side_effect=fake_post):
            outcome = decide_flow("retention", state)

        decisions = calls[0][1]
        chat = calls[1][1]
        self.assertEqual(decisions["model"], "typesafe/jev-1.13")
        self.assertNotIn("plugins", decisions)
        self.assertNotEqual(calls[0][0].rstrip("/").endswith("chat/completions"), True)
        self.assertIn("decisions", calls[0][0])
        self.assertEqual(chat["model"], "openrouter/auto")
        self.assertEqual(chat["session_id"], "learner-42")
        self.assertEqual(chat["plugins"], [{"id": "auto-router", "cost_tier": "max"}])
        self.assertEqual(outcome["generative_provider"], "openrouter")
        self.assertEqual(outcome["draft_model"], "anthropic/claude-sonnet-4.5")
        self.assertEqual(outcome["cost_tier"], "max")
        self.assertEqual(outcome["model"], "typesafe/jev-1.13-20260917")
        db = SessionLocal()
        try:
            row = (
                db.query(AgentDecision)
                .filter(AgentDecision.agent_name == "System1")
                .order_by(AgentDecision.id.desc())
                .first()
            )
        finally:
            db.close()
        self.assertIn("draft_model=anthropic/claude-sonnet-4.5", row.decision)
        stored = json.loads(row.gemini_prompt_summary)
        self.assertEqual(stored["draft_model"], "anthropic/claude-sonnet-4.5")
        self.assertEqual(stored["model"], "anthropic/claude-sonnet-4.5")
        self.assertEqual(stored["system1_model"], "typesafe/jev-1.13-20260917")

    def test_free_override_omits_the_auto_plugin(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test"
        os.environ["SYSTEM2_MODEL"] = "openrouter/free"
        captured = {}

        def fake_post(url, headers=None, json=None, timeout=None):
            captured["json"] = json
            return _FakeResponse(_chat_payload("Zero-cost draft."))

        with patch("httpx.post", side_effect=fake_post):
            outcome = decide_flow("tutor", tutor_state("???"))
        self.assertEqual(captured["json"]["model"], "openrouter/free")
        self.assertNotIn("plugins", captured["json"])
        self.assertEqual(outcome["text"], "Zero-cost draft.")

    def test_explicit_session_id_overrides_state_and_is_accepted_by_decide(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test"
        captured = {}

        def fake_post(url, headers=None, json=None, timeout=None):
            captured["json"] = json
            return _FakeResponse(_chat_payload("Sticky draft."))

        with patch("httpx.post", side_effect=fake_post):
            outcome = decide_flow(
                "tutor",
                {"question": "???", "session_id": "from-state"},
                session_id=" from-caller ",
            )
        self.assertEqual(captured["json"]["session_id"], "from-caller")
        self.assertEqual(outcome["session_id"], "from-caller")

        with patch("httpx.post", side_effect=fake_post):
            response = _CLIENT.post("/system1/decide", json={
                "state": {"question": "Explain this in a new way"},
                "flow": "tutor",
                "session_id": " tutor-session ",
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured["json"]["session_id"], "tutor-session")
        self.assertEqual(response.json()["session_id"], "tutor-session")

    def test_cost_tier_override_wins_over_urgency(self):
        os.environ["SYSTEM2_COST_TIER"] = "medium"
        answers = {
            "urgency": {
                "score": 2.0,
                "confidence": 0.99,
                "probabilities": {"0": 0.0, "1": 0.0, "2": 1.0},
            },
        }
        self.assertEqual(auto_cost_tier(answers), "medium")


class AutoCostTierTests(_EnvGuard):
    def test_missing_score_is_low(self):
        self.assertEqual(auto_cost_tier({}), "low")
        self.assertEqual(auto_cost_tier({"intent": {"choice": "open", "confidence": 0.2}}), "low")

    def test_urgency_bands_and_low_confidence_step_down(self):
        peaked = {"0": 0.0, "1": 0.0, "2": 1.0}
        self.assertEqual(auto_cost_tier({
            "urgency": {"score": 0.2, "confidence": 0.9, "probabilities": {"0": 0.9, "1": 0.1, "2": 0.0}},
        }), "low")
        self.assertEqual(auto_cost_tier({
            "urgency": {"score": 1.0, "confidence": 0.9, "probabilities": {"0": 0.0, "1": 1.0, "2": 0.0}},
        }), "high")
        self.assertEqual(auto_cost_tier({
            "urgency": {"score": 2.0, "confidence": 0.99, "probabilities": peaked},
        }), "max")
        self.assertEqual(auto_cost_tier({
            "urgency": {"score": 2.0, "confidence": 0.2, "probabilities": peaked},
        }), "xhigh")

    def test_urgency_wins_over_difficulty(self):
        self.assertEqual(auto_cost_tier({
            "difficulty": {"score": 0.0, "confidence": 0.9, "probabilities": {"0": 1, "1": 0, "2": 0}},
            "urgency": {"score": 2.0, "confidence": 0.9, "probabilities": {"0": 0, "1": 0, "2": 1}},
        }), "max")

    def test_session_id_uses_explicit_id_then_learner_id(self):
        self.assertIsNone(session_id_from_state("What is softmax?"))
        self.assertIsNone(session_id_from_state({"question": "???"}))
        self.assertEqual(session_id_from_state({"session_id": " conv-9 "}), "conv-9")
        self.assertEqual(
            session_id_from_state({"id": 42, "email": "slow@ent.dev", "phase": "01"}),
            "learner:42",
        )


class OpenRouterLiveSmokeTests(_EnvGuard):
    """``python -m web.system1.live`` is opt-in. Default CI never calls OpenRouter."""

    def _main(self):
        from web.system1.live import main
        return main

    def test_readme_documents_the_live_command_and_pinned_models(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("python -m web.system1.live --draft", readme)
        self.assertIn("typesafe/jev-1.13", readme)
        self.assertIn("System 2 default is `openrouter/auto`", readme)
        self.assertIn("Zero-cost override: `openrouter/free`", readme)
        self.assertIn("random free model", readme)
        self.assertIn("no Auto surcharge", readme)
        self.assertIn("auto-router", readme)
        self.assertIn("cost_tier", readme)
        self.assertIn("session_id", readme)
        self.assertIn("typesafe/jev-1.13", readme)

    def test_missing_key_skips_the_network(self):
        main = self._main()
        self.assertEqual(os.environ.get("OPENROUTER_API_KEY"), "")
        with patch("httpx.post", side_effect=AssertionError("unexpected network")) as mocked:
            code = main([])
        self.assertEqual(code, 2)
        self.assertEqual(mocked.call_count, 0)

    def test_jev_decision_uses_the_pinned_model_and_skips_chat_by_default(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-live"
        os.environ["SYSTEM1_BACKEND"] = "mock"
        main = self._main()
        captured = []

        def fake_post(url, headers=None, json=None, timeout=None):
            captured.append({"url": url, "headers": headers, "json": json})
            return _FakeResponse({
                "model": "typesafe/jev-1.13-20260917",
                "answers": {
                    "department": {
                        "type": "choice",
                        "choice": "billing",
                        "confidence": 0.95,
                        "probabilities": {"billing": 0.97, "technical": 0.03},
                    },
                    "needs_generation": {"type": "noul", "noul": 0.08},
                },
            })

        from io import StringIO
        stdout = StringIO()
        with patch("httpx.post", side_effect=fake_post), patch("sys.stdout", stdout):
            code = main([])
        self.assertEqual(code, 0)
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0]["url"], "https://openrouter.ai/api/alpha/decisions")
        self.assertEqual(captured[0]["json"]["model"], "typesafe/jev-1.13")
        self.assertEqual(captured[0]["headers"]["Authorization"], "Bearer sk-or-live")
        self.assertEqual(captured[0]["json"]["questions"]["department"]["type"], "choice")
        report = json.loads(stdout.getvalue())
        self.assertEqual(report["backend"], "openrouter_jev")
        self.assertEqual(report["jev_model"], "typesafe/jev-1.13")
        self.assertEqual(report["served_model"], "typesafe/jev-1.13-20260917")
        self.assertEqual(report["system2_model"], "openrouter/auto")
        self.assertEqual(report["cost_tier"], "low")
        self.assertEqual(report["answers"]["department"]["choice"], "billing")
        self.assertIsNone(report["draft"])
        self.assertNotIn("sk-or-live", stdout.getvalue())

    def test_draft_flag_calls_the_free_chat_model(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-live"
        main = self._main()
        captured = []

        def fake_post(url, headers=None, json=None, timeout=None):
            captured.append({"url": url, "json": json})
            if "decisions" in url:
                return _FakeResponse({
                    "model": "typesafe/jev-1.13-20260917",
                    "answers": {
                        "department": {
                            "type": "choice",
                            "choice": "billing",
                            "confidence": 0.95,
                            "probabilities": {"billing": 0.97, "technical": 0.03},
                        },
                        "needs_generation": {"type": "noul", "noul": 0.08},
                    },
                })
            return _FakeResponse(_chat_payload("Refund the duplicate charge."))

        from io import StringIO
        stdout = StringIO()
        before = _GEMINI_CALLS["n"]
        with patch("httpx.post", side_effect=fake_post), patch("sys.stdout", stdout):
            code = main(["--draft"])
        self.assertEqual(code, 0)
        self.assertEqual(_GEMINI_CALLS["n"], before)
        self.assertEqual(len(captured), 2)
        self.assertIn("/api/alpha/decisions", captured[0]["url"])
        self.assertIn("/chat/completions", captured[1]["url"])
        self.assertEqual(captured[1]["json"]["model"], "openrouter/auto")
        self.assertEqual(
            captured[1]["json"]["plugins"],
            [{"id": "auto-router", "cost_tier": "low"}],
        )
        self.assertNotIn("session_id", captured[1]["json"])
        report = json.loads(stdout.getvalue())
        self.assertEqual(report["draft"]["provider"], "openrouter")
        self.assertEqual(report["draft"]["model"], "openrouter/auto")
        self.assertEqual(report["draft"]["cost_tier"], "low")
        self.assertEqual(report["draft"]["text"], "Refund the duplicate charge.")
        self.assertNotIn("sk-or-live", stdout.getvalue())

    def test_jev_http_failure_is_nonzero_and_does_not_draft(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-live"
        main = self._main()
        calls = []

        def fake_post(url, headers=None, json=None, timeout=None):
            calls.append(url)
            return _FakeResponse({"error": "upstream"}, status_code=503)

        with patch("httpx.post", side_effect=fake_post):
            code = main(["--draft"])
        self.assertEqual(code, 1)
        self.assertEqual(calls, ["https://openrouter.ai/api/alpha/decisions"])


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
