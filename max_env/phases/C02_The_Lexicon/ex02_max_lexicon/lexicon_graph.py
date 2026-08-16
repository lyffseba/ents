"""MAX Graph identity over the Fangorn token IDs."""

from pathlib import Path

import numpy as np
from max import driver, engine
from max.dtype import DType
from max.graph import DeviceRef, Graph, TensorType


SAMPLE = "Fangorn"


def encode(text: str, sample: str = SAMPLE):
    chars = sorted(set(text))
    stoi = {ch: i for i, ch in enumerate(chars)}
    return np.array([stoi.get(c, 0) for c in sample], dtype=np.int64)


def forward(ids):
    return ids


def main():
    corpus = Path(__file__).resolve().parents[1] / "ex03_mojo_lexicon" / "input.txt"
    tokens = encode(corpus.read_text())
    graph = Graph(
        "lexicon",
        forward,
        input_types=[TensorType(DType.int64, (7,), DeviceRef.CPU())],
    )
    session = engine.InferenceSession(
        devices=driver.load_devices(driver.scan_available_devices())
    )
    model = session.load(graph)
    out = model.execute(tokens)
    print(np.from_dlpack(out[0]))


if __name__ == "__main__":
    main()
