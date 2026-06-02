from std.tensor import Tensor
import std.math

fn main():
    var logits = Tensor[DType.float32](3)
    logits[0] = -1.0
    logits[1] = -2.0
    logits[2] = 5.0

    var max_val = logits[0]
    for i in range(1, 3):
        if logits[i] > max_val:
            max_val = logits[i]

    var sum_exp: Float32 = 0.0
    var exps = Tensor[DType.float32](3)
    for i in range(3):
        exps[i] = math.exp(logits[i] - max_val)
        sum_exp += exps[i]

    var probs = Tensor[DType.float32](3)
    for i in range(3):
        probs[i] = exps[i] / sum_exp

    print(probs[0], probs[1], probs[2], sep=", ")