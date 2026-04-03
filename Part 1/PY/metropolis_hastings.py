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


#QUESTION B - gelman rubin diagonstic

# function to run a single chain
def run_chain(x0, N, s, seed=None):
    if seed is not None:
        np.random.seed(seed)
    
    x_vals = np.zeros(N + 1)
    x_vals[0] = x0
    
    for i in range(1, N + 1):
        x_star = np.random.normal(loc=x_vals[i-1], scale=s)
        log_r = log_f(x_star) - log_f(x_vals[i-1])
        u = np.random.uniform(0, 1)
        
        if np.log(u) < log_r:
            x_vals[i] = x_star
        else:
            x_vals[i] = x_vals[i-1]
    
    return x_vals[1:]  # dont need x0

# calcualte R hat
def calc_rhat(chains):
    J = len(chains)
    N = len(chains[0])
    
    # means and variances for each chainn
    M_j = np.array([np.mean(chain) for chain in chains])
    V_j = np.array([np.var(chain, ddof=1) for chain in chains])
    
    # within chain varaince
    W = np.mean(V_j)
    
    # overall mean
    M = np.mean(M_j)
    
    # between chain varience
    B = N / (J - 1) * np.sum((M_j - M)**2)
    
    # R hat formula
    R_hat = np.sqrt((B + W) / W)
    
    return R_hat

# part 1: calculate for N=2000, s=0.001, J=4
print("\n" + "="*60)
print("Part B: Gelman-Rubin Convergance Diagnostic")
print("="*60)

N_b = 2000
s_b = 0.001
J_b = 4
burnin = 500  # throw away first 500

print(f"\nParams: N={N_b}, s={s_b}, J={J_b}, burn-in={burnin}")

# use closer starting points so it doesnt blow up
init_vals = [-0.5, -0.2, 0.2, 0.5]
chains = []

print("\nRunning chains...")
for j in range(J_b):
    # run longer chain then cut off burnin
    full_chain = run_chain(x0=init_vals[j], N=N_b+burnin, s=s_b, seed=j*100)
    chain = full_chain[burnin:]
    chains.append(chain)
    print(f"  Chain {j+1}: x0={init_vals[j]}, mean={np.mean(chain):.4f}, std={np.std(chain, ddof=1):.4f}")

# compute R hat
rhat = calc_rhat(chains)
print(f"\nR-hat = {rhat:.6f}")
if rhat < 1.05:
    print("Converged! (R-hat < 1.05)")
else:
    print("NOT converged (R-hat >= 1.05)")

# part 2: plot R hat over different s values
print("\n" + "="*60)
print("Plotting R-hat for different s values...")
print("="*60)

s_vals = np.linspace(0.001, 1, 50)
rhat_vals = []

print("Computing... this takes a sec ahhhhhhhhh")
for idx, s_val in enumerate(s_vals):
    chains_s = []
    for j in range(J_b):
        full_chain = run_chain(x0=init_vals[j], N=N_b+burnin, s=s_val, seed=j*100)
        chain = full_chain[burnin:]
        chains_s.append(chain)
    
    rhat_s = calc_rhat(chains_s)
    rhat_vals.append(rhat_s)
    
    if (idx + 1) % 10 == 0:
        print(f"  {idx + 1}/{len(s_vals)} done")

print("Done computing!")

# make the plot
plt.figure(figsize=(12, 7))
plt.plot(s_vals, rhat_vals, 'b-', linewidth=2, label='R-hat')
plt.axhline(y=1.05, color='r', linestyle='--', linewidth=2, label='Convergence threshhold (1.05)')
plt.axhline(y=1.0, color='g', linestyle=':', linewidth=1.5, alpha=0.7, label='Perfect (1.0)')

# mark the s=0.001 point
s_001_idx = np.argmin(np.abs(s_vals - 0.001))
plt.plot(s_vals[s_001_idx], rhat_vals[s_001_idx], 'ro', markersize=10, 
         label=f's=0.001: R-hat={rhat_vals[s_001_idx]:.4f}')

plt.xlabel('Step size (s)', fontsize=12)
plt.ylabel('R-hat', fontsize=12)
plt.title(f'Gelman-Rubin Diagnostic (N={N_b}, J={J_b} chains)', fontsize=14)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('gelman_rubin_plot.png', dpi=300)
print("\nPlot saved as 'gelman_rubin_plot.png'")

# some stats
print(f"\nMin R-hat: {np.min(rhat_vals):.6f} at s={s_vals[np.argmin(rhat_vals)]:.4f}")
print(f"Max R-hat: {np.max(rhat_vals):.6f} at s={s_vals[np.argmax(rhat_vals)]:.4f}")
converged_cnt = np.sum(np.array(rhat_vals) < 1.05)
print(f"Converged s values: {converged_cnt}/{len(s_vals)}")

plt.show()


