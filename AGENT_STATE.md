# Ents — Memory Crystal

Read this first on a new machine. Update it when the stack or the curriculum contract changes.

## Now (2026-08-16)

- **Stack:** Pixi in `max_env/` on the **stable** Modular channel.
  - Mojo **1.0.0**
  - MAX **26.5.0**
  - Python **3.13**
  - MLX **0.29** (PyPI)
  - Platform: `osx-arm64` only
- **Curriculum contract:** `max_env/phases/curriculum.json` (human copy: `CURRICULUM.md`)
- **Phases that grade 4/4:** C00 Seed, C01 Enting, C02 Lexicon (JAX + MLX + MAX + Mojo)
- **Not written:** C03 Self-Attention, C04 GPT-2. **C05** is an admitted stub.
- **Surfaces:** `ents-cli/game.py` TUI, `web/` Academy (demo mode without Gemini), `ents-pi-mod/`
- **Git:** GitHub `main` is PR-protected. Hugging Face `hf` is a dataset remote.

## Grade

```bash
cd max_env && pixi install
../max_env/phases/C00_The_Seed/grademe.sh
../max_env/phases/C01_The_Enting/grademe.sh
../max_env/phases/C02_The_Lexicon/grademe.sh
./scripts/test_curriculum.py
./scripts/test_oracle_honest.sh
./scripts/test_cli_actions.py   # needs textual in .venv
```

Expect **4 pass, 0 fail, 0 skip** on C00–C02 after `pixi install`.

## Rules that must stay true

- Exercise dirs: `ex00` JAX, `ex01` MLX, `ex02` MAX, `ex03` Mojo.
- Graders never `echo` the expected answer on failure.
- MAX exercises use `max.graph`, not ONNX.
- Mojo 1.0: `def` not `fn`; import `std.math` / `std.pathlib`.
- MLX skip is only allowed when `import mlx` fails. On this pin it must pass.
- `_oracle.sh` rewrites relocated `modular.cfg` so Mojo can find `std`.

## Next (real work, not docs)

1. C03 The Sapling — self-attention, Four Pillars, same Oracle format.
2. Stop treating leftover GPT-2 ONNX (`scripts/download_gpt2.py`) as if MAX still loads it.
3. C05 is not production until it loads a real model.

---
When you finish a session: update **Now**, **Grade** results if they changed, and **Next**. Do not append another diary.
