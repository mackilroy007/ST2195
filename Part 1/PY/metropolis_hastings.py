import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

# ok so we need N=10000 and s=1 for the metropolis thing
x0 = 0.0  # starting point
N = 10000  # number of samples
s = 1.0  # step size or whatever

# array to hold all the x values
x_values = np.zeros(N + 1)
x_values[0] = x0

# target distribution - standard normal 
def f(x):
    # Target distribution: Standard Normal N(0,1)
    return np.exp(-0.5 * x**2) / np.sqrt(2 * np.pi)

# log version to avoid numerical issues (tip)
def log_f(x):
    # log of normal pdf, easier to compute
    return -0.5 * x**2 - 0.5 * np.log(2 * np.pi)

# Metropolis-Hastings algorithm
for i in range(1, N + 1):
    # Simulate a random number x* from Normal(x_{i-1}, s)
    x_star = np.random.normal(loc=x_values[i-1], scale=s)
    
    # Compute the ratio r(x*, x_{i-1}) = f(x*) / f(x_{i-1})
    log_r = log_f(x_star) - log_f(x_values[i-1]) #or / ??
    
    # random uniform for acceptance
    u = np.random.uniform(0, 1)
    
    # check if we accept (using log comparison)
    if np.log(u) < log_r:
        x_values[i] = x_star  # accept
    else:
        x_values[i] = x_values[i-1]  # reject, keep old value

        
#QUESTIONE: A

# drop the first value (x0) to get x1...xN
samples = x_values[1:]

# calculate monte carlo estimates
sample_mean = np.mean(samples)  # should be close to 0
sample_std = np.std(samples, ddof=1)  # should be close to 1

print(f"Sample mean (Monte Carlo estimate): {sample_mean:.4f}")
print(f"Sample std dev (Monte Carlo estimate): {sample_std:.4f}")

# make the plot with histogram and kde
plt.figure(figsize=(10, 6))

# histogram of samples
plt.hist(samples, bins=50, density=True, alpha=0.6, color='blue',
         label='Histogram', edgecolor='black')

# kernel density estimate
kde = gaussian_kde(samples)
x_range = np.linspace(samples.min(), samples.max(), 1000)
plt.plot(x_range, kde(x_range), 'r-', linewidth=2, label='KDE')

# overlay true f(x) for comparison
x_true = np.linspace(-4, 4, 1000)
y_true = f(x_true)
plt.plot(x_true, y_true, 'g--', linewidth=2, label='True f(x)')

plt.xlabel('x')
plt.ylabel('Density')
plt.title('Metropolis-Hastings: Histogram, KDE, and True Distribution')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('metropolis_results.png', dpi=300)
plt.show()

print("\nPlot saved as 'metropolis_results.png'")
