# 3x4 embedding, row-major. Token 2 is the sprout.
# Tensor API was removed from this Mojo nightly; List is the allowed container.

def main():
    var weights = List[Float32]()
    # row 0
    weights.append(0.1)
    weights.append(0.2)
    weights.append(0.3)
    weights.append(0.4)
    # row 1
    weights.append(-0.1)
    weights.append(-0.2)
    weights.append(-0.3)
    weights.append(-0.4)
    # row 2
    weights.append(0.5)
    weights.append(-0.2)
    weights.append(0.8)
    weights.append(0.1)

    var cols = 4
    var row = 2
    var off = row * cols
    print(weights[off], weights[off + 1], weights[off + 2], weights[off + 3], sep=", ")
