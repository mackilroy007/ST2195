import numpy as np

# Step 1: Set up initial values for the Metropolis-Hastings algorithm

# Initial value for the Markov chain
x0 = 0.0

# Number of iterations
N = 10000

# Step size parameter (controls the proposal distribution)
s = 1.0

# Initialize array to store the generated values
x_values = np.zeros(N + 1)
x_values[0] = x0

print(f"Initial value x0: {x0}")
print(f"Number of iterations N: {N}")
print(f"Step size parameter s: {s}")
print(f"\nArray initialized to store {N + 1} values")

