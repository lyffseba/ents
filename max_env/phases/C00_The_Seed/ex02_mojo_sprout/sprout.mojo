from std.tensor import Tensor

fn main():
    # 3x4 vocabulary embedding (matches ex00 JAX weights), row-major layout.
    var weights = Tensor[DType.float32](3, 4)

    weights[0, 0] = 0.1
    weights[0, 1] = 0.2
    weights[0, 2] = 0.3
    weights[0, 3] = 0.4

    weights[1, 0] = -0.1
    weights[1, 1] = -0.2
    weights[1, 2] = -0.3
    weights[1, 3] = -0.4

    weights[2, 0] = 0.5
    weights[2, 1] = -0.2
    weights[2, 2] = 0.8
    weights[2, 3] = 0.1

    comptime cols = 4
    comptime row = 2
    var row_offset = row * cols

    var ptr = weights.unsafe_ptr()
    print(
        ptr[row_offset + 0],
        ptr[row_offset + 1],
        ptr[row_offset + 2],
        ptr[row_offset + 3],
        sep=", ",
    )