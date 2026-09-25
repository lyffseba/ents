"""Confidence-gated System 1 bus for Ents Academy.

State plus typed questions (Choice / Score / Noul, sent to Laya as
choice / score / noul) become structured answers and a confidence score.
High confidence takes a deterministic route. Mid/low confidence, or a
``needs_generation`` noul, drafts with OpenRouter chat when a key is set
and otherwise uses the existing demo-safe generative fallback.

Every decision is written to ``agent_decisions`` and shown on ``/ops``.
"""

from .bus import decide, decide_flow, status

__all__ = ["decide", "decide_flow", "status"]
