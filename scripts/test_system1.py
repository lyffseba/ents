#!/usr/bin/env python3
"""System 1 decision bus tests.

Demo/mock mode: no Gemini key and no OpenRouter key. Covers the mock
backend, confidence gating, and the tutor plus retention flows.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

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
from web.system1.backends import laya_importable, predict, reset_backend_state  # noqa: E402
from web.system1.flows import tutor_state  # noqa: E402
from web.system1.gate import classify_route  # noqa: E402
from web.system1.questions import normalize_questions  # noqa: E402
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
            )
        }
        os.environ["SYSTEM1_BACKEND"] = "mock"
        os.environ["OPENROUTER_API_KEY"] = ""
        os.environ.pop("SYSTEM1_HIGH_CONFIDENCE", None)
        os.environ.pop("SYSTEM1_NEEDS_GENERATION", None)

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


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
