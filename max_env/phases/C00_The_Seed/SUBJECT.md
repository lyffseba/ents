# C00 - The Seed

*“You must understand the soil before you can grow the tree.”*

Summary: This document is the first module of the 77 AI Awakening. You will discover the basic building blocks of AI inference: Tensors, Embeddings, and Graph Compilation.

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
### Exercise 01: lore_roots

| Exercise 01 | |
| :--- | :--- |
| **Turn-in directory** | `ex01_max_roots/` |
| **Files to turn in** | `roots.py` |
| **Allowed functions** | `max.engine.InferenceSession`, `onnx.helper.*`, `print` |

*   Now, we compile this operation into a computational graph.
*   Write a script that constructs an ONNX model with a single `Gather` node (representing an embedding lookup) using the exact same weights as ex00.
*   Save the model as `soil.onnx`.
*   Initialize a Modular MAX `InferenceSession`, load the ONNX file, and execute it using the input `[2]`.
*   Output format must exactly match: `[[ 0.5 -0.2  0.8  0.1]]`

---

## Chapter III
### Exercise 02: lore_sprout

| Exercise 02 | |
| :--- | :--- |
| **Turn-in directory** | `ex02_mojo_sprout/` |
| **Files to turn in** | `sprout.mojo` |
| **Allowed functions** | `Tensor`, `print` |

*   Forget JAX. Forget Python. It's time to touch the bare metal.
*   Write a Mojo script that initializes a 2D `Tensor` representing the vocabulary weights from ex00.
*   Access the raw memory to pull the values for the 3rd row (index 2).
*   Print them out separated by commas.
*   Output format must exactly match: `0.5, -0.2, 0.8, 0.1`