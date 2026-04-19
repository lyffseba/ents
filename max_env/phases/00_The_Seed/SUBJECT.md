# 🌳 SUBJECT: 00_The_Seed

## The Lore
*“You must understand the soil before you can grow the tree.”*
Every ancient Ent started as a single, humble seed. In the world of language models, the seed is the **Bigram Model**, and its roots are the **Embedding Layer**. Before an Ent can speak, it must know how to translate a single thought (a token ID) into a feeling (a dense mathematical vector).

## The Pedagogy (School 42 Style)
This repository follows a strict, discovery-based learning methodology:
1. **No hand-holding:** You are given a goal, constraints, and allowed tools. The rest is up to you.
2. **Tri-Force mastery:** You must solve the problem in JAX (Math), MAX (Graph), and Mojo (Bare Metal).
3. **The Grader:** You must pass the automated tests. Run `./grademe.sh` to check your progress.

---

## Exercise 00: The Soil (JAX)
**Directory:** `ex00_jax_soil/`
**File to submit:** `soil.py`
**Allowed functions:** `jax.numpy.array`, `jax.numpy.take`

**Objective:**
A token is just an integer (e.g., `2`). An embedding matrix is a 2D grid of numbers. 
Your task is to write a JAX script that initializes a specific 3x4 embedding matrix (provided in the scaffold) and extracts the vector for token ID `2`.

**Expected Output:**
```
[ 0.5 -0.2  0.8  0.1]
```

---

## Exercise 01: The Roots (MAX)
**Directory:** `ex01_max_roots/`
**File to submit:** `roots.py`
**Allowed functions:** `max.engine.InferenceSession`, `onnx.helper` (provided)

**Objective:**
Now, we must compile this operation into a graph. We have provided a script that generates `soil.onnx`. Your task is to write a script that loads this ONNX file into the Modular MAX engine and runs inference on the input `[2]`.

**Expected Output:**
```
[[ 0.5 -0.2  0.8  0.1]]
```

---

## Exercise 02: The Sprout (Mojo)
**Directory:** `ex02_mojo_sprout/`
**File to submit:** `sprout.mojo`
**Allowed functions:** `Tensor`, `print`

**Objective:**
Forget JAX. Forget graphs. It's time to touch the bare metal.
Initialize a 1D Mojo `Tensor` representing the vocabulary. Write the raw memory access to pull the values for the 3rd row (index 2). 

**Expected Output:**
```
0.5, -0.2, 0.8, 0.1
```