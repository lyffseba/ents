import jax.numpy as jnp
import jax

def main():
    # 1. We are given the logits for the token "hello"
    logits = jnp.array([-1.0, -2.0, 5.0])
    
    # 2. Apply Softmax to convert to probabilities
    probs = jax.nn.softmax(logits)
    
    print(probs)

if __name__ == "__main__":
    main()
