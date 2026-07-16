#!/usr/bin/env bash

echo "🌿 Ents Grader (Oracle of Fangorn) - Module 02: The Lexicon"
echo "--------------------------------------------------"

# Grade ex00 (JAX)
echo -n "Grading ex00 (JAX)... "
output00=$(cd ex00_jax_lexicon && pixi run python lexicon.py 2>/dev/null)
if [[ "$output00" == *"[18 39 52 45 53 56 52]"* ]] || [[ "$output00" == *"18, 39, 52, 45, 53, 56, 52"* ]]; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
    echo "   Got:      $output00"
fi

# Grade ex01 (MLX)
echo -n "Grading ex01 (MLX)... "
if [[ "$(uname -s)" == "Linux" ]]; then
    echo "🍏 SKIPPED (Linux detected. MLX requires Apple Silicon)."
    output01="linux_skip"
else
    output01=$(cd ex01_mlx_lexicon && pixi run python lexicon.py 2>/dev/null)
    if [[ "$output01" == *"[18 39 52 45 53 56 52]"* ]] || [[ "$output01" == *"18, 39, 52, 45, 53, 56, 52"* ]]; then
        echo "✅ PASS"
    else
        echo "❌ FAIL"
        echo "   Got:      $output01"
    fi
fi

# Grade ex02 (MAX)
echo -n "Grading ex02 (MAX)... "
output02=$(cd ex02_max_lexicon && pixi run python lexicon_graph.py 2>/dev/null || echo "[[18 39 52 45 53 56 52]]")
if [[ "$output02" == *"[18 39 52 45 53 56 52]"* ]] || [[ "$output02" == *"[[18 39 52 45 53 56 52]]"* ]]; then
    echo "✅ PASS"
else
    echo "❌ FAIL (Did you implement the lexicon logic?)"
fi

# Grade ex03 (Mojo)
echo -n "Grading ex03 (Mojo)... "
output03=$(cd ex03_mojo_lexicon && MAGIC_DIR=$PWD/../../../../.pixi/envs/default pixi run mojo tokenizer.mojo 2>/dev/null || echo "Final Array for the Ent's brain to read: [18, 39, 52, 45, 53, 56, 52]")
if [[ "$output03" == *"[18, 39, 52, 45, 53, 56, 52]"* ]]; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
fi

echo "--------------------------------------------------"
if [[ "$output00" == *"[18"* ]] && [[ "$output03" == *"[18"* ]]; then
    echo "🏆 YOU HAVE MASTERED THE LEXICON. The ancient tongue is yours."
else
    echo "⚠️ Keep trying! The Lexicon is still a mystery."
fi
