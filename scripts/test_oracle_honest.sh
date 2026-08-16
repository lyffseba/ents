#!/usr/bin/env bash
# Prove the Oracle fails when a student program prints nothing / wrong output.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PHASE="$ROOT/max_env/phases/C00_The_Seed"
TARGET="$PHASE/ex00_jax_soil/soil.py"
BACKUP="$(mktemp)"
cp "$TARGET" "$BACKUP"
trap 'cp "$BACKUP" "$TARGET"; rm -f "$BACKUP"' EXIT

cat > "$TARGET" <<'PY'
print("I am not an embedding")
PY

out="$("$PHASE/grademe.sh" || true)"
echo "$out"
if echo "$out" | grep -q "Grading ex00 (JAX)... ❌ FAIL"; then
    echo "HONEST: broken JAX is rejected"
else
    echo "CHEAT: broken JAX was not rejected"
    exit 1
fi
if echo "$out" | grep -q "YOU HAVE PLANTED THE SEED"; then
    echo "CHEAT: trophy printed despite failures"
    exit 1
fi
echo "Oracle honesty check passed"
