import jax.numpy as jnp

def main():
    # The expected IDs for "Fangorn" are: [18, 39, 52, 45, 53, 56, 52]
    tokens = jnp.array([18, 39, 52, 45, 53, 56, 52])
    
    print(tokens)

if __name__ == "__main__":
    main()
