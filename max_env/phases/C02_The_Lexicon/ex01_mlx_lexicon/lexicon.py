import mlx.core as mx
from pathlib import Path

SAMPLE = "Fangorn"


def encode(text: str, sample: str = SAMPLE):
    chars = sorted(set(text))
    stoi = {ch: i for i, ch in enumerate(chars)}
    return mx.array([stoi.get(c, 0) for c in sample])


def main():
    corpus = Path(__file__).resolve().parents[1] / "ex03_mojo_lexicon" / "input.txt"
    text = corpus.read_text()
    print(encode(text))


if __name__ == "__main__":
    main()
