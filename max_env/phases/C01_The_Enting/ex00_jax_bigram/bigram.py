import jax
import jax.numpy as jnp


def main():
    # Vocab: ["<pad>", "hello", "world"]. Token "hello" is row 1.
    logits = jnp.array(
        [
            [0.0, 0.0, 0.0],
            [-1.0, -2.0, 5.0],
            [0.0, 0.0, 0.0],
        ]
    )
    hello_id = 1
    probs = jax.nn.softmax(logits[hello_id])
    print(probs)


if __name__ == "__main__":
    main()
