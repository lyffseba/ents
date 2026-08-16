# Trial of Fangorn — filesystem contract

One map. Human copy of `curriculum.json` (imported by CLI, web Oracle, and `ents-pi-mod`).

| Phase | Directory | JAX | MLX | MAX | Mojo | Grader |
|---|---|---|---|---|---|---|
| C00 Seed | `C00_The_Seed/` | `ex00_jax_soil/soil.py` | `ex01_mlx_branch/branch.py` | `ex02_max_roots/roots.py` | `ex03_mojo_sprout/sprout.mojo` | `grademe.sh` |
| C01 Enting | `C01_The_Enting/` | `ex00_jax_bigram/bigram.py` | `ex01_mlx_leaf/leaf.py` | `ex02_max_bigram/bigram_graph.py` | `ex03_mojo_bigram/bigram.mojo` | `grademe.sh` |
| C02 Lexicon | `C02_The_Lexicon/` | `ex00_jax_lexicon/lexicon.py` | `ex01_mlx_lexicon/lexicon.py` | `ex02_max_lexicon/lexicon_graph.py` | `ex03_mojo_lexicon/tokenizer.mojo` | `grademe.sh` |
| C03 Sapling | — | — | — | — | — | not written (self-attention) |
| C04 Treebeard | — | — | — | — | — | not written (GPT-2) |
| C05 Entmoot | `C05_The_Entmoot/` | — | — | stub only | — | no grader |

Rules:
- Exercise numbers are sequential: `ex00` JAX, `ex01` MLX, `ex02` MAX, `ex03` Mojo.
- Graders never print expected answers as a fallback.
- Stack: Modular 26.5 / Mojo 1.0 / MAX 26.5 on Python 3.13 so MLX wheels install. MLX is skipped (not passed) only if `import mlx` still fails.
- MAX exercises use `max.graph`, not ONNX.
- C02 corpus is `ex03_mojo_lexicon/input.txt`. Encode `Fangorn` → `[18, 39, 52, 45, 53, 56, 52]`.
