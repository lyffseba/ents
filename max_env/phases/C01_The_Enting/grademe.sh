#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
source "$(pwd)/../_oracle.sh"

echo "🌿 Ents Grader (Oracle of Fangorn) - Module 01: The Enting"
echo "--------------------------------------------------"

if oracle_wants jax; then
    output00="$(oracle_capture ex00_jax_bigram python bigram.py || true)"
    oracle_grade "ex00 (JAX)" "$output00" \
        "softmax([-1,-2,5]) ≈ [2.470376e-03 9.088005e-04 9.966208e-01]" \
        "[2.4703" "[0.002470" "[0.002428" "[2.470376e-03"
fi

if oracle_wants mlx; then
    oracle_mlx_or_skip "ex01 (MLX)" ex01_mlx_leaf leaf.py \
        "softmax([-1,-2,5]) ≈ [2.470376e-03 9.088005e-04 9.966208e-01]" \
        "[2.4703" "[0.002470" "[0.002428" "0.00247" "0.002428"
fi

if oracle_wants max; then
    output_max="$(oracle_capture ex02_max_bigram python bigram_graph.py || true)"
    oracle_grade "ex02 (MAX)" "$output_max" \
        "[[2.470376e-03 9.088005e-04 9.966208e-01]]" \
        "[2.4703" "[0.002470" "[0.002428" "[[2.470376e-03"
fi

if oracle_wants mojo; then
    output_mojo="$(oracle_capture_mojo ex03_mojo_bigram bigram.mojo || true)"
    oracle_grade "ex03 (Mojo)" "$output_mojo" \
        "0.002470, 0.000909, 0.996621 (or 0.002428, 0.000893, 0.996678)" \
        "0.002470" "0.002428" "2.470376e-03" "2.4703"
fi

oracle_summary "THE ENTING HAS SPOKEN. You are ready for Phase 02." \
    "Keep trying! The Enting remains silent."
