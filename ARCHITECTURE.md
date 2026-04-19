# 🌳 44 Architecture (The "Tri-Force" Approach)

To build a truly innovative from-scratch inference engine (inspired by Karpathy's `llm.c` and `nanoGPT`), we are utilizing a hybrid approach combining the elegance of mathematical research with bare-metal performance. 

This repository is designed as an **End-to-End Educational Journey** for AI engineers. We start from the absolute basics of language modeling and scale up to modern high-performance inference. 

> **The Theme: The Ents of AI 🌿**
> As we build these models, we acknowledge that one day, GPT-2 and GPT-3 will be viewed as ancient, towering, slow-speaking giants of the past—much like the **Ents** of Tolkien's Middle-earth. We are walking through Fangorn Forest, waking them up one by one, to learn their ancient secrets.

## The Core Stack
1. **JAX & Flax (The Ground Truth):** 
   - Used for mathematical reference, weight extraction, and verifying our tensor outputs. JAX gives us a pure, functional ground-truth implementation.
2. **Modular MAX (The Graph Engine):**
   - Used to compile high-level ONNX/PyTorch models directly to hardware to serve as our baseline performance metric.
3. **Mojo (The "llm.c" / "Rust" Layer):**
   - This is where the magic happens. We will write our custom tensors, memory management, and attention kernels in raw Mojo. This gives us C/Rust-level performance with Pythonic syntax.

## The Evolutionary Roadmap (Growing the Forest)
To deeply understand the architecture, we will build from the simplest concepts up to the 44 engine, implementing each phase across our "Tri-Force" stack (JAX -> MAX -> Mojo). **Each phase is designed as a self-guided, test-driven programming challenge (inspired by the trials of Fangorn Forest).**

1. **Phase 00: The Seed (Embedding Layer) 🌱**
   - *Challenge:* Given a token ID, retrieve its mathematical vector. 
   - *Goal:* Master JAX arrays, ONNX/MAX graph compilation, and bare-metal Mojo memory access.
2. **Phase 01: The Enting (Bigram Model) 🌿**
   - *Challenge:* Convert raw logits into probabilities using Softmax.
   - *Goal:* Predict the next token based only on the current token.
3. **Phase 02: GPT-1 (The Sapling / Quickbeam) 🌲**
   - The original OpenAI GPT (117M parameters). Introduces the core Self-Attention mechanism and positional embeddings. "Don't be hasty," but it's faster than what came before!
3. **Phase 3: GPT-2 (The Young Ent / Treebeard's Awakening) 🌲**
   - The 124M parameter model. We move LayerNorms to the input of each sub-block (pre-norm architecture) and expand the context window. It begins to speak with coherence.
4. **Phase 4: GPT-3 "Ada" to "Davinci" (The Ancient Forest) 🌳**
   - *Note: Ada, Babbage, Curie, and Davinci are actually GPT-3 models (scaling up to 175B parameters).* We will explore their architectural tweaks (like alternating dense and sparse attention patterns) at a smaller scale. These are the elder Ents.
5. **Phase 5: The Entmoot (Custom Engine) 🏔️**
   - Taking the best components of the above and writing hyper-optimized Flash Attention and matrix multiplication kernels in bare-metal Mojo. All the ancient wisdom comes together in an unstoppable march.

## How to Follow the Journey
For every Phase, the workflow is:
1. **Extract & Verify (JAX):** Load/build the model mathematically and establish the "ground truth" numbers.
2. **Compile & Run (MAX):** Export the model to ONNX, feed it into MAX, and establish the baseline performance speed.
3. **Build from Scratch (Mojo):** Write the underlying C-level math operations by hand in `.mojo` files to match the ground truth outputs while aiming to beat the MAX baseline speeds.

## Syncing Strategy
All development is tracked across two remotes:
- **Hugging Face (`hf`):** For datasets, weights, and public versioning.
- **GitHub (`origin`):** For CI/CD and open-source code collaboration.
*(A unified sync script is provided in `scripts/sync.sh`)*