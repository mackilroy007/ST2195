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

# Step 2: Define the target distribution for the Metropolis-Hastings algorithm

# Define the target distribution f(x)
# Using a standard normal distribution as the target
def f(x):
    """Target distribution: Standard Normal N(0,1)"""
    return np.exp(-0.5 * x**2) / np.sqrt(2 * np.pi)

# Metropolis-Hastings algorithm
for i in range(1, N + 1):
    # Simulate a random number x* from Normal(x_{i-1}, s)
    x_star = np.random.normal(loc=x_values[i-1], scale=s)
    
    # Compute the ratio r(x*, x_{i-1}) = f(x*) / f(x_{i-1})
    r = f(x_star) / f(x_values[i-1])
    
    # Generate a random number u from Uniform(0, 1)
    u = np.random.uniform(0, 1)
    
    # Accept or reject the proposal
    if u < r:
        # Accept: set x_i = x*
        x_values[i] = x_star
    else:
        # Reject: set x_i = x_{i-1}
        x_values[i] = x_values[i-1]

print(f"Generated {N} samples from the target distribution")
print(f"\n First 10 values: {x_values[:10]}")
print(f"Last 10 values: {x_values[-10:]}")
