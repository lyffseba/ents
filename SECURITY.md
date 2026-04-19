# Security Policy

## Supported Versions
This project is an educational framework (The AI Awakening). We intend to maintain this standalone module long-term with strict security protocols.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Isolation & Sandboxing
To ensure this repository remains perfectly secure and with no vulnerabilities:
1. **Dependency Pinning:** All execution environments are completely isolated using `pixi`. Dependencies (`jax`, `flax`, `modular`, `max`) are strictly version-pinned in `pixi.toml` to prevent supply-chain attacks.
2. **Model Safety:** Downloaded model weights (e.g., ONNX, PyTorch files) are strictly ignored by version control (`max_env/models/` in `.gitignore`) and are never executed directly via unsafe deserialization (e.g., raw `pickle`). We compile models natively via `max.engine` and `ONNX`.
3. **Bare Metal Execution:** Mojo code interacts directly with memory. The `grademe.sh` Oracle is designed to test modules without running `eval()` or injecting unchecked variables.

## Reporting a Vulnerability
If you discover a security vulnerability within `ents`, please do NOT open a public issue.
Instead, send a direct message or open a private advisory via GitHub under the `lyffseba/ents` repository. We aim to address critical execution or dependency vulnerabilities within 48 hours.