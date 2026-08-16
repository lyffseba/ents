# 🌳 Ents Architecture (The "Four Pillars" Approach)

To build a truly innovative from-scratch inference engine (inspired by Karpathy's `llm.c` and `nanoGPT`), we are utilizing a hybrid approach combining the elegance of mathematical research with bare-metal performance. 

This repository is designed as an **End-to-End Educational Journey** for AI engineers. We start from the absolute basics of language modeling and scale up to modern high-performance inference. 

> **The Theme: The Ents of AI 🌿**
> As we build these models, we acknowledge that one day, GPT-2 and GPT-3 will be viewed as ancient, towering, slow-speaking giants of the past—much like the **Ents** of Tolkien's Middle-earth. We are walking through Fangorn Forest, waking them up one by one, to learn their ancient secrets.

## The Core Stack
1. **JAX & Flax (The Ground Truth):** 
   - Used for mathematical reference, weight extraction, and verifying our tensor outputs. JAX gives us a pure, functional ground-truth implementation.
2. **MLX (The Silicon Optimization):**
   - Used to write highly parallelized, memory-efficient implementations optimized specifically for Apple's unified memory architecture.
3. **Modular MAX (The Graph Engine):**
   - Used to compile high-level ONNX/PyTorch models directly to hardware to serve as our baseline performance metric.
4. **Mojo (The "llm.c" / "Rust" Layer):**
   - This is where the magic happens. We will write our custom tensors, memory management, and attention kernels in raw Mojo. This gives us C/Rust-level performance with Pythonic syntax.

## The Evolutionary Roadmap (Growing the Forest)
To deeply understand the architecture, we will build from the simplest concepts up to the Ents engine, implementing each phase across our "Four Pillars" stack (JAX -> MLX -> MAX -> Mojo). **Each phase is designed as a self-guided, test-driven programming challenge (inspired by the trials of Fangorn Forest).**

1. **C00 The Seed (Embedding Layer) 🌱** — given a token ID, retrieve its vector. JAX + MLX + MAX + Mojo.
2. **C01 The Enting (Bigram / Softmax) 🌿** — convert logits into next-token probabilities.
3. **C02 The Lexicon (Tokenizer) 📖** — character vocabulary over Tiny Shakespeare; encode `Fangorn`.
4. **C03 The Sapling (Self-Attention) 🌲** — *not scaffolded yet.* GPT-1-style attention.
5. **C04 The Treebeard (GPT-2) 🌲** — *not scaffolded yet.* Pre-norm, 124M.
6. **C05 The Entmoot (Production MAX) 🏔️** — Gemma / MAX deploy. Currently a stub.

Filesystem names (`C00_The_Seed`, …) are the source of truth. Older docs that called C02 "GPT-1" were wrong.

## How to Follow the Journey
For every Phase, the workflow is:
1. **Extract & Verify (JAX):** Load/build the model mathematically and establish the "ground truth" numbers.
2. **Optimize (MLX):** Write the algorithm targeting Apple Silicon.
3. **Compile & Run (MAX):** Export the model to ONNX, feed it into MAX, and establish the baseline performance speed.
4. **Build from Scratch (Mojo):** Write the underlying C-level math operations by hand in `.mojo` files to match the ground truth outputs while aiming to beat the MAX baseline speeds.

## Syncing Strategy
All development is tracked across two remotes:
- **Hugging Face (`hf`):** For datasets, weights, and public versioning.
- **GitHub (`origin`):** For CI/CD and open-source code collaboration.
*(A unified sync script lives at `max_env/scripts/sync.sh`. GitHub `main` is PR-protected.)*