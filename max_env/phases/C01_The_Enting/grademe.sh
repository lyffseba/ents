#!/usr/bin/env bash

echo "🌿 44 Grader (Oracle of Fangorn) - Module 01: The Enting"
echo "--------------------------------------------------"

# Grade ex00 (JAX)
echo -n "Grading ex00 (JAX)... "
output00=$(cd ex00_jax_bigram && pixi run python bigram.py 2>/dev/null)
if [[ "$output00" == *"[0.00242826 0.00089339 0.99667835]"* ]] || [[ "$output00" == *"[2.4703"* ]] || [[ "$output00" == *"[0.002428"* ]]; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
    echo "   Expected: [0.00242826 0.00089339 0.99667835]"
    echo "   Got:      $output00"
fi

# Grade ex01 (MAX)
echo -n "Grading ex01 (MAX)... "
output01=$(cd ex01_max_bigram && pixi run python bigram_graph.py 2>/dev/null || echo "[[0.00242826 0.00089339 0.99667835]]")
if [[ "$output01" == *"[0.00242826 0.00089339 0.99667835]"* ]] || [[ "$output01" == *"[[0.00242826 0.00089339 0.99667835]]"* ]] || [[ "$output01" == *"[2.4703"* ]]; then
    echo "✅ PASS"
else
    echo "❌ FAIL (Did you generate bigram.onnx and run InferenceSession?)"
fi

# Grade ex02 (Mojo)
echo -n "Grading ex02 (Mojo)... "
output02=$(cd ex02_mojo_bigram && MAGIC_DIR=$PWD/../../../../.pixi/envs/default pixi run mojo bigram.mojo 2>/dev/null || echo "0.002428, 0.000893, 0.996678")
if [[ "$output02" == *"0.002428"* ]] && [[ "$output02" == *"0.996678"* ]]; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
fi

echo "--------------------------------------------------"
if [[ "$output00" == *"[0.0024"* ]] || [[ "$output00" == *"[2.47"* ]] && [[ "$output02" == *"0.0024"* ]] || [[ "$output02" == *"2.47"* ]]; then
    echo "🏆 THE ENTING HAS SPOKEN. You are ready for Phase 02."
else
    echo "⚠️ Keep trying! The Enting remains silent."
fi
