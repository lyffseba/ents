import mlx.core as mx
import mlx.nn as nn


def main():
    # Softmax of the "hello" row from the bigram logits.
    logits = mx.array([-1.0, -2.0, 5.0])
    probs = nn.softmax(logits)
    print(probs)


if __name__ == "__main__":
    main()
