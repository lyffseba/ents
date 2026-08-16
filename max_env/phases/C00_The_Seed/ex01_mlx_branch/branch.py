import mlx.core as mx


def main():
    # Same 3x4 embedding as the JAX soil: token 2 is the sprout.
    weights = mx.array(
        [
            [0.1, 0.2, 0.3, 0.4],
            [-0.1, -0.2, -0.3, -0.4],
            [0.5, -0.2, 0.8, 0.1],
        ]
    )
    token_id = 2
    output_vector = weights[token_id]
    print(output_vector)


if __name__ == "__main__":
    main()
