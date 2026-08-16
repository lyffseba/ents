#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
source "$(pwd)/../_oracle.sh"

echo "🌿 Ents Grader (Oracle of Fangorn) - Module 01: The Enting"
echo "--------------------------------------------------"

# float32 and float64 softmax([-1,-2,5]) both accepted; empty output is not.
output00="$(oracle_capture ex00_jax_bigram python bigram.py || true)"
oracle_grade "ex00 (JAX)" "$output00" \
    "softmax([-1,-2,5]) ≈ [2.470376e-03 9.088005e-04 9.966208e-01]" \
    "[2.4703" "[0.002470" "[0.002428" "[2.470376e-03"

oracle_mlx_or_skip "ex01 (MLX)" ex01_mlx_leaf leaf.py \
    "softmax([-1,-2,5]) ≈ [2.470376e-03 9.088005e-04 9.966208e-01]" \
    "[2.4703" "[0.002470" "[0.002428" "0.00247" "0.002428"

output_max="$(oracle_capture ex01_max_bigram python bigram_graph.py || true)"
oracle_grade "ex02 (MAX)" "$output_max" \
    "[[2.470376e-03 9.088005e-04 9.966208e-01]]" \
    "[2.4703" "[0.002470" "[0.002428" "[[2.470376e-03"

output_mojo="$(oracle_capture_mojo ex02_mojo_bigram bigram.mojo || true)"
oracle_grade "ex03 (Mojo)" "$output_mojo" \
    "0.002470, 0.000909, 0.996621 (or 0.002428, 0.000893, 0.996678)" \
    "0.002470" "0.002428" "2.470376e-03" "2.4703"

oracle_summary "THE ENTING HAS SPOKEN. You are ready for Phase 02." \
    "Keep trying! The Enting remains silent."
