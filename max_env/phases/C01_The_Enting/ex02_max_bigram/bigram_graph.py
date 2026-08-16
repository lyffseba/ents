"""MAX Graph: gather the 'hello' logit row, then softmax."""

import numpy as np
from max import driver, engine
from max.dtype import DType
from max.graph import DeviceRef, Graph, TensorType, ops


LOGITS = np.array(
    [
        [0.0, 0.0, 0.0],
        [-1.0, -2.0, 5.0],
        [0.0, 0.0, 0.0],
    ],
    dtype=np.float32,
)


def forward(idx):
    table = ops.constant(LOGITS, dtype=DType.float32, device=DeviceRef.CPU())
    row = ops.gather(table, idx, axis=0)
    return ops.softmax(row)


def main():
    graph = Graph(
        "bigram",
        forward,
        input_types=[TensorType(DType.int64, (1,), DeviceRef.CPU())],
    )
    session = engine.InferenceSession(
        devices=driver.load_devices(driver.scan_available_devices())
    )
    model = session.load(graph)
    out = model.execute(np.array([1], dtype=np.int64))
    print(np.from_dlpack(out[0]))


if __name__ == "__main__":
    main()
