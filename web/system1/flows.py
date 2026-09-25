"""Question sets and deterministic copy for Academy flows that use the gate."""

from __future__ import annotations

import json
from typing import Any, Callable

from .backends import state_text

DraftBuilder = Callable[[Any, dict, str], tuple[str, str]]
Renderer = Callable[[Any, dict], str]

TUTOR_QUESTIONS = {
    "intent": {
        "type": "choice",
        "instructions": "What kind of help does this Fangorn learner need?",
        "criteria": {
            "define": "asking what a named concept is, such as softmax, embedding, bigram, tokenizer, or attention",
            "hint": "stuck on an exercise and wants a nudge toward the next step",
            "lore": "asking about the Ents story or Fangorn trials",
            "open": "open-ended question that needs a generated explanation",
        },
    },
    "difficulty": {
        "type": "score",
        "instructions": "How hard is this question for a Fangorn learner?",
        "criteria": [
            "recall a definition or what something is",
            "apply a procedure while stuck on an exercise",
            "derive a new result that needs a generated explanation",
        ],
    },
    "needs_generation": {
        "type": "noul",
        "instructions": "Does this case need a personalized written message instead of a fixed template?",
    },
}

RETENTION_QUESTIONS = {
    "intervention": {
        "type": "choice",
        "instructions": "Which retention action fits this stalled learner?",
        "criteria": {
            "nudge": "learner stuck for several days on a phase and needs a short encouraging nudge",
            "discount": "learner threatens to cancel, quit, or wants a refund, so offer a Pro discount",
            "tutor_handoff": "learner asks what a named concept is, rather than a check-in",
            "wait": "learner just started today and it is too early to intervene",
        },
    },
    "urgency": {
        "type": "score",
        "instructions": "How urgent is the intervention?",
        "criteria": [
            "can wait, they just started",
            "nudge this week, stuck for several days",
            "intervene today, blocking or about to cancel",
        ],
    },
    "churn_risk": {
        "type": "noul",
        "instructions": "Is this learner likely to cancel, quit, or abandon the trial?",
    },
    "needs_generation": {
        "type": "noul",
        "instructions": "Does this case need a personalized written message instead of a fixed template?",
    },
}

_GLOSSARY = {
    "softmax": (
        "Softmax turns a vector of logits into probabilities that sum to 1: "
        "exp(x_i) / sum_j exp(x_j). In C01 (The Enting) you write that reduction "
        "in JAX, MLX, MAX, and Mojo. Check the axis you sum over, and the "
        "off-by-one when the expected string is fixed."
    ),
    "embedding": (
        "An embedding is a table from token id to vector. C00 (The Seed) asks "
        "you to look up one row. The id is an index, not a coordinate, and the "
        "row length is the model width from SUBJECT.md."
    ),
    "bigram": (
        "A bigram model predicts the next token from the current one. C01 turns "
        "those logits into a distribution with softmax. Grade one pillar at a "
        "time so a MAX failure does not hide a correct JAX answer."
    ),
    "tokenizer": (
        "C02 (The Lexicon) is a character tokenizer over Tiny Shakespeare. "
        "Encode the word Fangorn and compare the id list to the grader, "
        "including the exact length."
    ),
    "attention": (
        "Self-attention is not scaffolded yet (C03, The Sapling). Until that "
        "chapter exists, finish softmax and the lexicon so the shapes you will "
        "attend over are already familiar."
    ),
}


def tutor_state(question: str) -> dict:
    return {"question": question}


def retention_state(user: dict) -> dict:
    text = (
        f"User {user['id']} ({user['email']}) has been at phase {user['phase']} "
        f"for {user['days']} days, stuck on: {user['stuck_on']}."
    )
    return {
        "id": user["id"],
        "email": user["email"],
        "phase": user["phase"],
        "days": user["days"],
        "stuck_on": user["stuck_on"],
        "text": text,
    }


def render_tutor(state: Any, answers: dict) -> str:
    question = state_text(state).lower()
    intent = str((answers.get("intent") or {}).get("choice") or "")
    if intent == "define":
        for term, blurb in _GLOSSARY.items():
            if term in question:
                return blurb
        return (
            "Name the tensor shapes in the current SUBJECT.md, then restate the "
            "definition in one sentence before you write code."
        )
    if intent == "hint":
        return (
            "Compare your output to the expected string in SUBJECT.md. Check the "
            "reduction axis and any off-by-one in the sum. One hint only — the "
            "Oracle wants your implementation."
        )
    if intent == "lore":
        return (
            "Fangorn is patient. Start at C00_The_Seed, grade with grademe.sh, "
            "and ask for a hint rather than a full solution."
        )
    return (
        "Restate the question as a shape and an expected output, then try the "
        "JAX pillar before MAX or Mojo."
    )


def render_retention(state: Any, answers: dict) -> str:
    fields = state if isinstance(state, dict) else {}
    phase = fields.get("phase", "?")
    days = fields.get("days", "?")
    stuck = fields.get("stuck_on", "this step")
    action = str((answers.get("intervention") or {}).get("choice") or "nudge")
    templates = {
        "nudge": (
            f"The forest noticed you have been at phase {phase} for {days} days, "
            f"stuck on {stuck}. Write the tensor shape before the reduction, then "
            f"rerun the Oracle on that pillar only."
        ),
        "discount": (
            f"You have been away from phase {phase}. Come back this week and Pro "
            f"is 20% off while you finish {stuck}."
        ),
        "tutor_handoff": (
            f"This looks like a concept gap on {stuck}. Ask Treebeard at /tutor "
            f"for a hint, not a full solution, then retry the phase {phase} lab."
        ),
        "wait": "No outreach. The learner has not been stalled long enough to intervene.",
    }
    return templates.get(action, templates["nudge"])


def render_raw(_state: Any, answers: dict) -> str:
    lines = ["System 1 routed this without a generative model."]
    for name, answer in answers.items():
        if "choice" in answer:
            lines.append(f"{name}: {answer['choice']}")
        elif "score" in answer:
            lines.append(f"{name}: {float(answer['score']):.2f}")
        elif "noul" in answer:
            lines.append(f"{name}: {float(answer['noul']):.2f}")
    return "\n".join(lines)


def draft_tutor(state: Any, answers: dict, reason: str) -> tuple[str, str]:
    system = (
        "You are Treebeard, wise Ent tutor for the Fangorn Trials. Help the "
        "learner master JAX/MLX/MAX/Mojo LLM internals. Give hints, not full "
        "solutions unless they are stuck."
    )
    prompt = (
        f"Learner question: {state_text(state)}\n"
        f"System 1 escalated ({reason}).\n"
        f"System 1 answers: {json.dumps(answers, default=str)}\n"
        "Answer in at most two short paragraphs."
    )
    return system, prompt


def draft_retention(state: Any, answers: dict, reason: str) -> tuple[str, str]:
    system = "You are the Entmoot Retention Agent. Be wise, ancient, and data-driven."
    prompt = (
        f"Learner state: {json.dumps(state, default=str)}\n"
        f"System 1 escalated ({reason}).\n"
        f"System 1 answers: {json.dumps(answers, default=str)}\n"
        "Write a 2-sentence nudge plus one micro-hint from the Fangorn Trials. "
        "Mention 20% off Pro only if churn risk is high."
    )
    return system, prompt


def draft_raw(state: Any, answers: dict, reason: str) -> tuple[str, str]:
    system = (
        "You are Treebeard. Use the System 1 notes as a decision, and do not "
        "invent facts that are absent from the state."
    )
    prompt = (
        f"System 1 escalated ({reason}).\n"
        f"State: {state_text(state)}\n"
        f"Answers: {json.dumps(answers, default=str)}\n"
        "Write a short reply the Academy can show to a learner or operator."
    )
    return system, prompt


FLOWS: dict[str, dict] = {
    "tutor": {
        "questions": TUTOR_QUESTIONS,
        "render": render_tutor,
        "draft": draft_tutor,
    },
    "retention": {
        "questions": RETENTION_QUESTIONS,
        "render": render_retention,
        "draft": draft_retention,
    },
}


def get_flow(name: str) -> dict:
    try:
        return FLOWS[name]
    except KeyError as exc:
        known = ", ".join(sorted(FLOWS))
        raise KeyError(f"unknown system1 flow {name!r} (expected {known})") from exc
