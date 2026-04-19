# C01 - The Enting

*“A single seed cannot speak. It must learn the probability of the next word.”*

Summary: In this module, you will build a Bigram Language Model. You will learn about Logits, Softmax, and probabilities.

## General Rules
*   Your exercises must be done in the exact directories specified.
*   You must strictly name your files as requested.
*   You must pass the Moulinette (`grademe.sh`). If it fails, your grade is 0.

---

## Chapter I
### Exercise 00: ft_jax_bigram

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
*   Output format must exactly match: `[0.00242826 0.00089339 0.99667835]`

---

## Chapter II
### Exercise 01: ft_max_bigram

| Exercise 01 | |
| :--- | :--- |
| **Turn-in directory** | `ex01_max_bigram/` |
| **Files to turn in** | `bigram_graph.py` |
| **Allowed functions** | `max.engine.InferenceSession`, `onnx.helper.*`, `print` |

*   Construct an ONNX computational graph that performs a `Gather` (embedding lookup) followed by a `Softmax`.
*   Pass the input token `[1]` through the graph.
*   Output the probabilities from the MAX engine.
*   Output format must exactly match: `[[0.00242826 0.00089339 0.99667835]]`

---

## Chapter III
### Exercise 02: ft_mojo_bigram

| Exercise 02 | |
| :--- | :--- |
| **Turn-in directory** | `ex02_mojo_bigram/` |
| **Files to turn in** | `bigram.mojo` |
| **Allowed functions** | `Tensor`, `math.exp`, `print` |

*   Write a bare-metal Mojo script that manually calculates the Softmax of the array `[-1.0, -2.0, 5.0]`.
*   Print the calculated probabilities separated by commas.
*   Output format must closely match: `0.002428, 0.000893, 0.996678`