# C01 - The Enting

*“A single seed cannot speak. It must learn the probability of the next word.”*

Summary: In this module, you will build a Bigram Language Model. You will learn about Logits, Softmax, and probabilities.

**If you have never coded AI before:**
When an AI tries to guess the next word, it spits out raw, messy scores called "Logits" (e.g., `[-1.0, 5.0]`). A higher score means it likes that word more. To turn these messy scores into clean percentages (like `1%` and `99%`), we use a math function called **Softmax**. Your job is to build that math function.

## General Rules
*   Your exercises must be done in the exact directories specified.
*   You must strictly name your files as requested.
*   You must pass the Oracle of Fangorn (`grademe.sh`). If it fails, your grade is 0.

---

## Chapter I
### Exercise 00: lore_jax_bigram

| Exercise 00 | |
| :--- | :--- |
| **Turn-in directory** | `ex00_jax_bigram/` |
| **Files to turn in** | `bigram.py` |
| **Allowed functions** | `jax.numpy.*`, `jax.nn.softmax`, `print` |

*   A bigram model predicts the next token based only on the current token.
*   You are given a vocab size of 3: `["<pad>", "hello", "world"]`
*   The token ID for "hello" is `1`.
*   Create a JAX script that initializes a token transition matrix (logits) of shape `(3, 3)`.
    *   Row 1 (the logits for "hello") should be `[-1.0, -2.0, 5.0]`.
*   Apply the softmax function to Row 1 to convert the logits into probabilities.
*   Print the resulting probability array.
*   Output format must exactly match: `[2.470376e-03 9.088005e-04 9.966208e-01]`

---

## Chapter II
### Exercise 01: lore_mlx_leaf

| Exercise 01 | |
| :--- | :--- |
| **Turn-in directory** | `ex01_mlx_leaf/` |
| **Files to turn in** | `leaf.py` |
| **Allowed functions** | `mlx.core.array`, `mlx.nn.softmax`, `print` |

*   Repeat the softmax of `[-1.0, -2.0, 5.0]` with MLX.
*   Print the probability array. Same numeric target as JAX.
*   On Linux the Oracle skips this pillar.

---

## Chapter III
### Exercise 02: lore_max_bigram

| Exercise 02 | |
| :--- | :--- |
| **Turn-in directory** | `ex02_max_bigram/` |
| **Files to turn in** | `bigram_graph.py` |
| **Allowed functions** | `max.engine.InferenceSession`, `max.graph.Graph`, `max.graph.ops.gather`, `max.graph.ops.softmax`, `print` |

*   Build a MAX Graph: gather row `1` of the 3x3 logit table, then softmax.
*   Pass input token `[1]` through the compiled graph.
*   Output must contain the softmax of `[-1.0, -2.0, 5.0]`.

---

## Chapter IV
### Exercise 03: lore_mojo_bigram

| Exercise 03 | |
| :--- | :--- |
| **Turn-in directory** | `ex03_mojo_bigram/` |
| **Files to turn in** | `bigram.mojo` |
| **Allowed functions** | `List`, `math.exp`, `print` |

*   Manually compute a numerically stable softmax of `[-1.0, -2.0, 5.0]` in Mojo.
*   Print the probabilities separated by commas.
*   Output format must closely match: `0.002470, 0.000909, 0.996621`