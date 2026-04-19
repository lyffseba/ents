# 🤖 44 - Continuous Development State
> *This file is used to hand off context and next steps between AI coding sessions.*

## Current Status (2026-04-18)
- **Project Goal:** Building a highly secure, standalone educational AI inference engine (`44`) focusing on the evolutionary history of LLMs (from Bigram up to Gemma 4), themed around the **Ents of Middle-earth** 🌳.
- **Project Scope:** `44` is the core Awakening repository. Standalone CLI and Pi Mod repositories will be built in the future to interact with this core.
- **Environment:** Pixi is set up in `max_env` with strict dependencies (`max`, `modular`, `jax`, `flax`, and `onnx`).
- **Milestones Achieved:**
  - Renamed all platforms (GitHub, Hugging Face) to `44`.
  - Implemented the C00 module (The Seed) complete with solutions and the Oracle of Fangorn grader (`grademe.sh`).
  - Scaffolded the C01 module (The Enting / Bigram Softmax).
  - Implemented strict security policies and sandboxing via `.gitignore` and `SECURITY.md`.

## Repository Sync Note
- The main code is properly tracked in Git. The `.pixi/` environments and downloaded `models/` are ignored.
- **To sync to Hugging Face (`lyffseba/44`):** `git push hf main`
- **To sync to GitHub (`lyffseba/44`):** `git push origin main`

## 🚀 NEXT STEPS FOR THE AGENT
1. **Solve C01 (The Enting):** Write the JAX, MAX, and Mojo Softmax code for `max_env/phases/C01_The_Enting/`. 
2. **Update the C01 Grader:** Finish writing `grademe.sh` for C01 so the student can verify their math.
3. **Spin-off Planning:** Outline the architecture for the `44-cli` game or `44-pi-mod` in dedicated markdown files to prepare for separating the projects.

---
*Agent Instructions:* When starting a new session, read this file to understand where the project left off. When completing a task, update the "Current Status" and "Next Steps" sections accordingly.