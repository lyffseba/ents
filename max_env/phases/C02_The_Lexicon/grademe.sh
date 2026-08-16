#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
source "$(pwd)/../_oracle.sh"

echo "🌿 Ents Grader (Oracle of Fangorn) - Module 02: The Lexicon"
echo "--------------------------------------------------"

output00="$(oracle_capture ex00_jax_lexicon python lexicon.py || true)"
oracle_grade "ex00 (JAX)" "$output00" "[18 39 52 45 53 56 52]" \
    "[18 39 52 45 53 56 52]" "18, 39, 52, 45, 53, 56, 52"

oracle_mlx_or_skip "ex01 (MLX)" ex01_mlx_lexicon lexicon.py \
    "[18 39 52 45 53 56 52]" \
    "[18 39 52 45 53 56 52]" "18, 39, 52, 45, 53, 56, 52"

output_max="$(oracle_capture ex02_max_lexicon python lexicon_graph.py || true)"
oracle_grade "ex02 (MAX)" "$output_max" "[18 39 52 45 53 56 52]" \
    "[18 39 52 45 53 56 52]" "[[18 39 52 45 53 56 52]]" "18, 39, 52, 45, 53, 56, 52"

output_mojo="$(oracle_capture_mojo ex03_mojo_lexicon tokenizer.mojo || true)"
oracle_grade "ex03 (Mojo)" "$output_mojo" "[18, 39, 52, 45, 53, 56, 52]" \
    "[18, 39, 52, 45, 53, 56, 52]"

oracle_summary "YOU HAVE MASTERED THE LEXICON. The ancient tongue is yours." \
    "Keep trying! The Lexicon is still a mystery."
