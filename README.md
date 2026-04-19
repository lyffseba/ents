# 🌳 77: The Awakening

Welcome, traveler. 

If you are reading this, you have decided to look behind the curtain of modern Artificial Intelligence. **77** is the master repository—a standalone, ultra-secure, from-scratch educational framework that merges the wisdom of MLX, MAX, JAX, and bare-metal Mojo. It is designed to take you from absolute zero to mastering the bare-metal architecture of modern language models (like GPT, LLaMA, and Gemma).

We are going to wake up the ancient language models one by one, like the Ents of Middle-earth, mastering their secrets from the ground up.

---

## ✈️ The "Airplane Mode" Checklist (Do this before you fly!)
This repository is designed to be completely offline-capable. If you are about to board an airplane and want to learn AI during your flight, run these commands **while you still have internet**:

1. **Install Pixi** (Our secure environment manager):
   ```bash
   curl -fsSL https://pixi.sh/install.sh | bash
   ```
2. **Download the offline environment** (This fetches JAX, Mojo, and Modular MAX):
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
3. 🕸️ **MAX (The Graph):** You will compile that math into a computational graph (ONNX) and run it through Modular's high-speed AI engine.
4. 🦀 **Mojo (The Bare Metal):** Finally, you will rewrite the operation in bare-metal Mojo, directly manipulating memory and pointers to achieve C-level speed.

For every module, you must write code for all four paradigms. You cannot progress until the automated grader (the `Oracle of Fangorn`) gives you a green `✅ PASS`.

---

## 🗺️ The Curriculum
Your journey takes place inside the `max_env/phases/` directory. Start at Chapter 00.

*   👉 [**C00 - The Seed**](max_env/phases/C00_The_Seed/SUBJECT.md): Tensors, memory access, and the Embedding Layer.
*   👉 [**C01 - The Enting**](max_env/phases/C01_The_Enting/SUBJECT.md): Logits, Softmax, and probabilities.
*   👉 [**C02 - The Lexicon**](max_env/phases/C02_The_Lexicon/SUBJECT.md): Tokenization, Data Preparation, and the Atomic GPT.
*   *C03 - The Sapling (Coming Soon): Self-Attention.*
*   *C04 - The Treebeard (Coming Soon): The full GPT-2 architecture.*
*   👉 [**C05 - The Entmoot**](max_env/phases/C05_The_Entmoot/SUBJECT.md): Deploying Gemma models in Production with MAX.

### How to test your code
Whenever you think you have solved a module, open your terminal and run the grader:
```bash
cd max_env/phases/C00_The_Seed
./grademe.sh
```

---

## The 77 Universe
This repository (`77`) is the **Master Core Educational Engine**. In the future, this universe will expand into:
1. **`77-cli`:** A standalone terminal RPG game where you play through the modules to "wake the Ents".
2. **`77-pi-mod`:** A standalone extension for Pi (the coding agent) to interact with these models locally.

Good luck. The forest awaits.
