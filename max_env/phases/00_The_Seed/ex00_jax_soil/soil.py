import jax.numpy as jnp

def main():
    # 1. The Embedding Matrix (Vocab Size: 3, Embedding Dim: 4)
    # Row 0 (Token 0): [ 0.1,  0.2,  0.3,  0.4]
    # Row 1 (Token 1): [-0.1, -0.2, -0.3, -0.4]
    # Row 2 (Token 2): [ 0.5, -0.2,  0.8,  0.1]
    
    # TODO: Initialize the weights matrix using jnp.array
    weights = None 
    
    # TODO: Define the token ID we want to look up
    token_id = None
    
    # TODO: Use JAX to extract the vector for token_id
    # Hint: jnp.take or simple indexing
    output_vector = None
    
    print(output_vector)

if __name__ == "__main__":
    main()
