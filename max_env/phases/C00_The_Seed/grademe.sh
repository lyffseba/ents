#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
source "$(pwd)/../_oracle.sh"

echo "🌿 Ents Grader (Oracle of Fangorn) - Module 00: The Seed"
echo "--------------------------------------------------"

output00="$(oracle_capture ex00_jax_soil python soil.py || true)"
oracle_grade "ex00 (JAX)" "$output00" "[ 0.5 -0.2  0.8  0.1]" \
    "[ 0.5 -0.2  0.8  0.1]" "[0.5 -0.2  0.8  0.1]"

oracle_mlx_or_skip "ex01 (MLX)" ex01_mlx_branch branch.py \
    "[ 0.5 -0.2  0.8  0.1]" \
    "[ 0.5 -0.2  0.8  0.1]" "[0.5 -0.2  0.8  0.1]" "0.5, -0.2, 0.8, 0.1"

output_max="$(oracle_capture ex01_max_roots python roots.py || true)"
oracle_grade "ex02 (MAX)" "$output_max" "[[ 0.5 -0.2  0.8  0.1]]" \
    "[[ 0.5 -0.2  0.8  0.1]]" "[[ 0.5 -0.2 0.8 0.1]]" "[[0.5 -0.2 0.8 0.1]]"

output_mojo="$(oracle_capture_mojo ex02_mojo_sprout sprout.mojo || true)"
oracle_grade "ex03 (Mojo)" "$output_mojo" "0.5, -0.2, 0.8, 0.1" \
    "0.5, -0.2, 0.8, 0.1"

oracle_summary "YOU HAVE PLANTED THE SEED. You are ready for Phase 01." \
    "Keep trying! The soil is not yet ready."
