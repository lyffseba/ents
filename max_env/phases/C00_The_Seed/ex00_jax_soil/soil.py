import jax.numpy as jnp

def main():
    # 1. The Embedding Matrix (Vocab Size: 3, Embedding Dim: 4)
    # Row 0 (Token 0): [ 0.1,  0.2,  0.3,  0.4]
    # Row 1 (Token 1): [-0.1, -0.2, -0.3, -0.4]
    # Row 2 (Token 2): [ 0.5, -0.2,  0.8,  0.1]
    
    weights = jnp.array([
        [ 0.1,  0.2,  0.3,  0.4],
        [-0.1, -0.2, -0.3, -0.4],
        [ 0.5, -0.2,  0.8,  0.1]
    ])
    
    token_id = 2
    
    output_vector = weights[token_id]
    
    print(output_vector)

if __name__ == "__main__":
    main()
