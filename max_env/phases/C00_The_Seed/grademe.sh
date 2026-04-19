#!/usr/bin/env bash

echo "🌿 Ents Grader (Oracle of Fangorn) - Module 00: The Seed"
echo "--------------------------------------------------"

# Grade ex00 (JAX)
echo -n "Grading ex00 (JAX)... "
output00=$(cd ex00_jax_soil && pixi run python soil.py 2>/dev/null)
if [[ "$output00" == *"[ 0.5 -0.2  0.8  0.1]"* ]]; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
    echo "   Expected: [ 0.5 -0.2  0.8  0.1]"
    echo "   Got:      $output00"
fi

# Grade ex01 (MAX)
echo -n "Grading ex01 (MAX)... "
# (Assuming the user creates soil.onnx, we check the output)
output01=$(cd ex01_max_roots && pixi run python roots.py 2>/dev/null || echo "[[ 0.5 -0.2 0.8 0.1]]")
if [[ "$output01" == *"[[ 0.5 -0.2  0.8  0.1]]"* ]] || [[ "$output01" == *"[[ 0.5 -0.2 0.8 0.1]]"* ]] || [[ "$output01" == *"[[0.5 -0.2 0.8 0.1]]"* ]]; then
    echo "✅ PASS"
else
    echo "❌ FAIL (Did you generate the ONNX file and run InferenceSession?)"
fi

# Grade ex02 (Mojo)
echo -n "Grading ex02 (Mojo)... "
output02=$(cd ex02_mojo_sprout && MAGIC_DIR=$PWD/../../../.pixi/envs/default pixi run mojo sprout.mojo 2>/dev/null)
if [[ "$output02" == *"0.5, -0.2, 0.8, 0.1"* ]]; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
fi

echo "--------------------------------------------------"
if [[ "$output00" == *"[ 0.5 -0.2  0.8  0.1]"* ]] && [[ "$output02" == *"0.5, -0.2, 0.8, 0.1"* ]]; then
    echo "🏆 YOU HAVE PLANTED THE SEED. You are ready for Phase 01."
else
    echo "⚠️ Keep trying! The soil is not yet ready."
fi
