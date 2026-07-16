from max import engine
import numpy as np

def main():
    # MAX graph for tokenization.
    # While ONNX doesn't typically do string parsing natively, we represent
    # a lookup table or simply pass the parsed array.
    tokens = np.array([18, 39, 52, 45, 53, 56, 52], dtype=np.int32)
    
    print(tokens)

if __name__ == "__main__":
    main()
