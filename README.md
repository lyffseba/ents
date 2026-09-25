# 🌳 Ents: The Awakening

> **🚀 OFFICIAL SUBMISSION — Build with Gemini XPRIZE**
>
> **Project:** Ents Academy (Ents: The Awakening — AI-Native Education Platform)
> **Category:** Education & Human Potential
> **Repo:** https://github.com/lyffseba/ents (or this local clone)
> **Demo (when deployed):** [INSERT CLOUD RUN URL]
> **Video:** [INSERT YOUTUBE/VIMEO <3min LINK — see VIDEO_SCRIPT.md]
>
> **For Judges (quick start):**
> 1. **See the live AI-native business in action:** Deployed version runs Gemini agents continuously. Local: follow "XPRIZE Contest Build" section below.
> 2. Go to `/ops` (or deployed equivalent) → click "trigger-retention" or "trigger-content". Watch Gemini make a real decision and log it (this is "AI executes key business decisions").
> 3. Go to `/tutor` and ask a question. A System 1 gate answers high-confidence prompts directly; open questions still call Gemini or OpenRouter when a key is set.
> 4. Evidence package: `xprize_evidence/`, `SUBMISSION.md`, `scripts/export_revenue.py`, agent logs in DB + /ops.
> 5. Full curriculum + Oracle: the `max_env/phases/` + `grademe.sh` (graders still pass).
>
> **Repo sharing for judging:** If private, add collaborators: `testing@devpost.com` and `judging@hacker.fund`.
>
> **One-line description:** The AI-native school where Gemini agents run the entire business (tutoring, retention, content creation) while teaching students to build real LLMs from scratch across JAX/MLX/MAX/Mojo.
>
> See `SUBMISSION.md` for the full narrative, checklist, and evidence. We are using Google Cloud Run (hosting + scaling) + Gemini API (multiple calls in deployed paths) as required.

**This is the live project built to win the Build with Gemini XPRIZE.**

Welcome, traveler. 

If you are reading this, you have decided to look behind the curtain of modern Artificial Intelligence. **Ents** is the master repository—a standalone, ultra-secure, from-scratch educational framework that merges the wisdom of MLX, MAX, JAX, and bare-metal Mojo. It is designed to take you from absolute zero to mastering the bare-metal architecture of modern language models (like GPT, LLaMA, and Gemma).

We are going to wake up the ancient language models one by one, like the Ents of Middle-earth, mastering their secrets from the ground up.

---

## ✈️ The "Airplane Mode" Checklist (Do this before you fly!)
This repository is designed to be completely offline-capable. If you are about to board an airplane and want to learn AI during your flight, run these commands **while you still have internet**:

1. **Install Pixi** (Our secure environment manager):
   ```bash
   curl -fsSL https://pixi.sh/install.sh | bash
   ```
2. **Download the offline environment** (Mojo 1.0, MAX 26.5, JAX, MLX):
   ```bash
   cd max_env
   pixi install
   ```
3. **Download the ancient weights** (Fetches the offline GPT-2 model):
   ```bash
   pixi run python scripts/download_gpt2.py
   ```
*You are now completely self-sufficient. Close your laptop, board your flight, and read on.*

---

## 📖 How to Read This Book (The Pedagogy)
This is not a standard tutorial. This is a **Trial of Fangorn** (an interactive, constraint-based learning journey). 
There is no hand-holding. You will be given a specific mathematical goal, strict constraints, and allowed functions.

To truly understand how AI works, you must master the **"Four Pillars"**:
1. 🧮 **JAX (The Math):** You will first write the raw math in Python. This is the theoretical ground truth.
2. 🍎 **MLX (The Silicon):** You will optimize the math specifically for Apple Silicon architecture.
3. 🕸️ **MAX (The Graph):** You will build a `max.graph` program and run it through Modular MAX 26.5.
4. 🦀 **Mojo (The Bare Metal):** Finally, you will rewrite the operation in bare-metal Mojo, directly manipulating memory and pointers to achieve C-level speed.

For every module, you must write code for all four paradigms. You cannot progress until the automated grader (the `Oracle of Fangorn`) gives you a green `✅ PASS`.

---

## 🗺️ The Curriculum
Your journey takes place inside the `max_env/phases/` directory. The path contract is [`CURRICULUM.md`](max_env/phases/CURRICULUM.md). Start at Chapter 00.

*   👉 [**C00 - The Seed**](max_env/phases/C00_The_Seed/SUBJECT.md): Embeddings across JAX, MLX, MAX, Mojo.
*   👉 [**C01 - The Enting**](max_env/phases/C01_The_Enting/SUBJECT.md): Softmax / bigram across all four pillars.
*   👉 [**C02 - The Lexicon**](max_env/phases/C02_The_Lexicon/SUBJECT.md): Character tokenizer; encode `Fangorn`.
*   *C03 - The Sapling (not written): Self-Attention.*
*   *C04 - The Treebeard (not written): GPT-2.*
*   👉 [**C05 - The Entmoot**](max_env/phases/C05_The_Entmoot/SUBJECT.md): Production MAX / Gemma (stub).

### How to test your code
Whenever you think you have solved a module, open your terminal and run the grader:
```bash
cd max_env/phases/C00_The_Seed
./grademe.sh
```

---

## The Ents Universe
This repository is both the curriculum and the XPRIZE surface:

1. **`max_env/phases/`** — Trial of Fangorn. Grade with `./grademe.sh`.
2. **`ents-cli/game.py`** — Textual RPG over those same files (`python ents-cli/game.py`).
3. **`web/`** — Ents Academy (FastAPI). Demo mode works without API keys: `make -C web smoke` (System 1 uses the mock backend).
4. **`ents-pi-mod/`** — Pi coding-agent extension (early).
5. **[`docs/STACK.md`](docs/STACK.md)** — stack ledger: pins, how each piece is used, latest stable official docs, and drift.

C03 (Self-Attention) and C04 (GPT-2) are not written yet. C05 is a production stub.

---

## System 1 decision bus

Tutor asks and the retention agent pass through a confidence-gated System 1 layer before any generative call. You send application **state** plus typed questions. Laya and TypeSafe Jev both speak three primitives; this bus uses Laya's names on the wire:

| You write | Wire type | Answer |
| --- | --- | --- |
| Choice | `choice` | selected label, per-option probabilities, confidence |
| Score | `score` | probability-weighted level on your ordered rubric, confidence |
| Noul | `noul` | `P(true)`. A question named `needs_generation` forces a draft when that probability is at least `SYSTEM1_NEEDS_GENERATION` (default 0.5). |

The gate then:

1. **High confidence** (every routing choice, and `needs_generation` when it is confidently false, at or above `SYSTEM1_HIGH_CONFIDENCE`, default 0.85) takes a **deterministic** template. No LLM.
2. **Mid/low confidence**, or `needs_generation` above the threshold, drafts with **OpenRouter chat** (`POST /api/v1/chat/completions`) when `OPENROUTER_API_KEY` is set. The default model is the free router `openrouter/free`. With no key, that call is skipped and the existing demo/Gemini path answers so the Academy still runs.

Every decision is stored in `agent_decisions` (`agent_name=System1`) and listed on `/ops` with a SYSTEM 1 badge. `GET /system1/status` reports which backend would run without loading weights. `POST /system1/decide` accepts either `"flow": "tutor"|"retention"` or your own `questions`.

### Environment

| Variable | Role |
| --- | --- |
| `SYSTEM1_BACKEND` | `laya` (default when unset), `openrouter_jev`, or `mock`. Unset prefers local Laya and falls back to the mock heuristic if the package or weights are missing, so CI and demo mode stay green. |
| `OPENROUTER_API_KEY` | TypeSafe Jev on OpenRouter (`typesafe/jev-1.13` via `POST /api/alpha/decisions`) and System 2 chat drafts. Omit it for demo mode: Jev falls back to the mock, and escalations skip OpenRouter. |
| `SYSTEM1_JEV_MODEL` | Jev model id. Default `typesafe/jev-1.13` (current Decisions API id; `~typesafe/jev-latest` tracks the newest release). |
| `SYSTEM2_MODEL` | OpenRouter chat model used only after the gate escalates. Default `openrouter/free`. Set a pinned `:free` model to choose one. |
| `SYSTEM1_HIGH_CONFIDENCE` | Deterministic cutoff. Default `0.85`. |
| `SYSTEM1_NEEDS_GENERATION` | Noul cutoff for a question named `needs_generation`. Default `0.5`. |
| `SYSTEM1_LAYA_MODEL` | Optional checkpoint: `english`, `multilingual`, or `typed-decisions`. |
| `SYSTEM1_LAYA_DEVICE` | `cpu`, `cuda`, or `mps`. |
| `SYSTEM1_LAYA_PRELOAD` | `1` to load Laya checkpoints at first use instead of lazily. |

### Try it

Demo / CI (no keys, no weights):

```bash
make -C web smoke
```

That target sets `SYSTEM1_BACKEND=mock` and runs `scripts/test_system1.py` (mock backend, confidence gate, tutor and retention) before the HTTP smoke. "What is softmax?" on `/tutor` is a deterministic glossary hit. An empty or ambiguous ask escalates to the demo draft. `POST /ops/trigger-retention` gates the stalled-learner nudge and logs it on `/ops`.

Local Laya (downloads the checkpoint on first predict, about 800MB for English):

```bash
pip install laya
export SYSTEM1_BACKEND=laya
# optional: export SYSTEM1_LAYA_DEVICE=cpu
make -C web run
```

If `import laya` fails or the weights cannot be loaded, that process falls back to the mock and records the reason on the decision.

Jev on OpenRouter, plus chat drafts for low-confidence cases.

A key is free to create: sign in at [openrouter.ai](https://openrouter.ai/) and create one at [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys). You do not need a separate TypeSafe account. Jev itself is billed per input token on that key (output tokens are free; price is on the [Jev 1.13 model page](https://openrouter.ai/typesafe/jev-1.13)). System 2 drafts default to [`openrouter/free`](https://openrouter.ai/openrouter/free), which routes to a zero-price model, so an escalation does not require a paid chat model. Pin one with `SYSTEM2_MODEL` (any model id ending in `:free`) when you want a specific free model instead of the router.

```bash
export OPENROUTER_API_KEY=sk-or-...   # from https://openrouter.ai/settings/keys
export SYSTEM1_BACKEND=openrouter_jev # mock | laya | openrouter_jev
export SYSTEM1_JEV_MODEL=typesafe/jev-1.13   # or ~typesafe/jev-latest
export SYSTEM2_MODEL=openrouter/free         # or e.g. a pinned model:free
make -C web run
```

Compare with mock (no key, no network — the same path CI runs):

```bash
export SYSTEM1_BACKEND=mock
unset OPENROUTER_API_KEY
make -C web smoke
```

`GET /system1/status` shows `requested_backend`, whether a key is set, and the Jev and System 2 model ids without calling either API.

A direct decision:

```bash
curl -s localhost:8000/system1/decide -H 'content-type: application/json' -d '{
  "state": "What is softmax?",
  "flow": "tutor"
}'
```

Good luck. The forest awaits.
