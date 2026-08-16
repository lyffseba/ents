# C00 - The Seed

*“You must understand the soil before you can grow the tree.”*

Summary: This document is the first module of the Ents AI Awakening. You will discover the basic building blocks of AI inference: Tensors, Embeddings, and Graph Compilation.

**If you have never coded AI before:**
Do not panic. A "Tensor" is just a grid of numbers (like an Excel spreadsheet). An "Embedding" is just a lookup table that turns a word (like "apple") into a row of numbers so the computer can do math on it. 

Your goal in this module is simple: find the row of numbers for Token ID `2`.

## General Rules
*   Your exercises must be done in the exact directories specified.
*   You must strictly name your files as requested.
*   You are only allowed to use the functions explicitly listed in the "Allowed functions" section.
*   You must pass the Oracle of Fangorn (`grademe.sh`). If it fails, your grade is 0.
*   If you have a question, read the ancient scrolls. If you still have a question, ask a fellow traveler.

---

## Chapter I
### Exercise 00: lore_soil

| Exercise 00 | |
| :--- | :--- |
| **Turn-in directory** | `ex00_jax_soil/` |
| **Files to turn in** | `soil.py` |
| **Allowed functions** | `jax.numpy.array`, `jax.numpy.take`, `print` |

*   An embedding matrix is a 2D grid of numbers. A token is just an integer index.
*   Write a Python script using JAX that initializes a 3x4 embedding matrix:
    *   Row 0: `[ 0.1,  0.2,  0.3,  0.4]`
    *   Row 1: `[-0.1, -0.2, -0.3, -0.4]`
    *   Row 2: `[ 0.5, -0.2,  0.8,  0.1]`
*   Your script must extract and print the exact vector for token ID `2`.
*   Output format must exactly match: `[ 0.5 -0.2  0.8  0.1]`

---

## Chapter II
### Exercise 01: lore_branch

| Exercise 01 | |
| :--- | :--- |
| **Turn-in directory** | `ex01_mlx_branch/` |
| **Files to turn in** | `branch.py` |
| **Allowed functions** | `mlx.core.array`, `print` |

*   Repeat the embedding lookup on Apple Silicon with MLX.
*   Same 3x4 weights and token ID `2` as the JAX soil.
*   Output must contain: `[ 0.5 -0.2  0.8  0.1]` (or the comma-separated form).
*   On Linux the Oracle skips this pillar.

---

## Chapter III
### Exercise 02: lore_roots

| Exercise 02 | |
| :--- | :--- |
| **Turn-in directory** | `ex02_max_roots/` |
| **Files to turn in** | `roots.py` |
| **Allowed functions** | `max.engine.InferenceSession`, `max.graph.Graph`, `max.graph.ops.gather`, `print` |

*   Compile the same embedding lookup as a MAX Graph (`ops.gather` over the 3x4 table).
*   Execute it with input `[2]`.
*   Output format must contain: `[[ 0.5 -0.2  0.8  0.1]]`
*   Current MAX nightlies do **not** load ONNX. Do not submit an `.onnx` file.

---

## Chapter IV
### Exercise 03: lore_sprout

| Exercise 03 | |
| :--- | :--- |
| **Turn-in directory** | `ex03_mojo_sprout/` |
| **Files to turn in** | `sprout.mojo` |
| **Allowed functions** | `List`, `print` |

*   Forget JAX. Forget Python. Store the 3x4 table in a row-major `List[Float32]`.
*   Read the four values of row index `2`.
*   Print them separated by commas.
*   Output format must exactly match: `0.5, -0.2, 0.8, 0.1`