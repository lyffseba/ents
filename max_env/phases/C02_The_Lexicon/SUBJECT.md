# C02 - The Lexicon

*“Before you can speak the ancient tongue, you must learn to read its letters.”*

Summary: A computer cannot read the letter `A`. It only understands numbers. You will build a character-level tokenizer that turns Tiny Shakespeare into token IDs, then encode the word `Fangorn`.

The corpus lives at `ex03_mojo_lexicon/input.txt` (already present for airplane mode). Your encoder must:

1. Take the unique characters of the corpus.
2. Sort them.
3. Map each character to its index.
4. Encode `Fangorn`.

Expected IDs: `[18, 39, 52, 45, 53, 56, 52]`

## General Rules
*   Exercises must live in the listed directories with the listed filenames.
*   Pass the Oracle of Fangorn (`grademe.sh`). If it fails, your grade is 0.
*   Do not hardcode the IDs. Build the vocabulary from the corpus.
*   On Linux, the MLX pillar is skipped.

---

## Chapter I
### Exercise 00: lore_jax_lexicon

| Exercise 00 | |
| :--- | :--- |
| **Turn-in directory** | `ex00_jax_lexicon/` |
| **Files to turn in** | `lexicon.py` |
| **Allowed functions** | `jax.numpy.array`, file I/O, `print` |

*   Read `../ex03_mojo_lexicon/input.txt`.
*   Build the sorted character vocabulary and encode `Fangorn`.
*   Output must contain: `[18 39 52 45 53 56 52]`

---

## Chapter II
### Exercise 01: lore_mlx_lexicon

| Exercise 01 | |
| :--- | :--- |
| **Turn-in directory** | `ex01_mlx_lexicon/` |
| **Files to turn in** | `lexicon.py` |
| **Allowed functions** | `mlx.core.array`, file I/O, `print` |

*   Same vocabulary and word as Chapter I, using MLX arrays.

---

## Chapter III
### Exercise 02: lore_max_lexicon

| Exercise 02 | |
| :--- | :--- |
| **Turn-in directory** | `ex02_max_lexicon/` |
| **Files to turn in** | `lexicon_graph.py` |
| **Allowed functions** | `max.engine.InferenceSession`, `max.graph.Graph`, file I/O, `print` |

*   Encode `Fangorn` from the corpus, then pass the integer vector through a MAX Graph identity.
*   Print the engine output. It must contain the same seven IDs.

---

## Chapter IV
### Exercise 03: lore_mojo_lexicon

| Exercise 03 | |
| :--- | :--- |
| **Turn-in directory** | `ex03_mojo_lexicon/` |
| **Files to turn in** | `tokenizer.mojo` |
| **Allowed functions** | `Path`, `List`, `print` (no Python interop, no `exec`) |

*   Read `input.txt` in this directory.
*   Encode `Fangorn` with the same sorted-character vocabulary.
*   Output must contain: `[18, 39, 52, 45, 53, 56, 52]`

The corpus file is checked in so airplane mode does not need a download.
