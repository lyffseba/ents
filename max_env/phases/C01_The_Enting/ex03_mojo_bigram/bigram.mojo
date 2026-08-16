from std import math


def main():
    var logits = List[Float32]()
    logits.append(-1.0)
    logits.append(-2.0)
    logits.append(5.0)

    var max_val = logits[0]
    for i in range(1, len(logits)):
        if logits[i] > max_val:
            max_val = logits[i]

    var sum_exp: Float32 = 0.0
    var exps = List[Float32]()
    for i in range(len(logits)):
        var e = math.exp(logits[i] - max_val)
        exps.append(e)
        sum_exp += e

    print(exps[0] / sum_exp, exps[1] / sum_exp, exps[2] / sum_exp, sep=", ")
