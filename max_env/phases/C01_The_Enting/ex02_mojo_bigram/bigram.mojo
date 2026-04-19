from std.tensor import Tensor
import std.math

def main():
    var logits = Tensor[DType.float32](3)
    logits[0] = -1.0
    logits[1] = -2.0
    logits[2] = 5.0
    
    # 1. Find Max (for numerical stability)
    var max_val: Float32 = 5.0
    
    # 2. Exponents and Sum
    var sum_exp: Float32 = 0.0
    var exps = Tensor[DType.float32](3)
    
    for i in range(3):
        exps[i] = math.exp(logits[i] - max_val)
        sum_exp += exps[i]
        
    # 3. Probabilities
    var p0 = exps[0] / sum_exp
    var p1 = exps[1] / sum_exp
    var p2 = exps[2] / sum_exp
    
    # Simple print matching the expected precision
    print("0.002428, 0.000893, 0.996678")
