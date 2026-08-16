"""MAX Graph embedding lookup. ONNX is no longer a MAX input format."""

import numpy as np
from max import driver, engine
from max.dtype import DType
from max.graph import DeviceRef, Graph, TensorType, ops


WEIGHTS = np.array(
    [
        [0.1, 0.2, 0.3, 0.4],
        [-0.1, -0.2, -0.3, -0.4],
        [0.5, -0.2, 0.8, 0.1],
    ],
    dtype=np.float32,
)


def forward(idx):
    table = ops.constant(WEIGHTS, dtype=DType.float32, device=DeviceRef.CPU())
    return ops.gather(table, idx, axis=0)


def main():
    graph = Graph(
        "soil",
        forward,
        input_types=[TensorType(DType.int64, (1,), DeviceRef.CPU())],
    )
    session = engine.InferenceSession(
        devices=driver.load_devices(driver.scan_available_devices())
    )
    model = session.load(graph)
    out = model.execute(np.array([2], dtype=np.int64))
    print(np.from_dlpack(out[0]))


if __name__ == "__main__":
    main()
