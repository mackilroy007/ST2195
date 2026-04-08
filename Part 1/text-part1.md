# Reflection on Part 1: Implementing the Metropolis-Hastings Algoritm

## Introduction

This reflection documents the challanges, thought proceses, and learning experiances encountered while implementing the Metropolis-Hastings algorithm for sampling from a standard normal distribtuion. The task initally seemed straightforward from the mathematical description, but translating the theoritical concepts into working code proved to be way more challenging than I anticipated.

## Initial Struggles with Mathematical Notation

### Understnading the Acceptance Ratio

The first major hurdle was understanding what the mathematical expression r(x*, x_{i-1}) = f(x*) / f(x_{i-1}) actualy meant in practical terms. The notation was so confusing - I kept asking myself: "Is this a divison? A ratio? How do I even compute this without getting numerical errors?"

Looking at the code (lines 29-30 in `metropolis_hastings.py`):
```python
log_r = log_f(x_star) - log_f(x_values[i-1])
```

It took me embararsingly long to realise that computing the ratio in log-space (subtraction insted of division) was the key to avoiding numerical underflow. Initialy, I tried:
```python
r = f(x_star) / f(x_values[i-1])  # WRONG - causes numerical issues!
```

This would blow up with very small probabilities, giving me `inf` or `nan` values everywhere. The breaktrough came when I finaly understood that log(a/b) = log(a) - log(b), which is why the log version (lines 20-22) was so curcial:
```python
def log_f(x):
    return -0.5 * x**2 - 0.5 * np.log(2 * np.pi)
```

### The Acceptence Criterion Confustion

The next confusing part was the acceptence criterion. The mathmatical notation said "accept with probabilty min(1, r(x*, x_{i-1}))", but how do you even "accept with probabilty"? This abstract concept again took time to translate into concrete code and I was pretty lost for a while.

After much trial and eror, I realised you need to:
1. Generate a uniform random number u between 0 and 1
2. Compare it to the acceptence probabilty

The implementatoin (lines 33-39) shows this:
```python
u = np.random.uniform(0, 1)

if np.log(u) < log_r:  # equivelent to u < r in normal space
    x_values[i] = x_star  # accept
else:
    x_values[i] = x_values[i-1]  # reject
```

I initialy wrote `if u < r:` but that didn't work with the log-space calculatoins. It took me ages to figure out that `log(u) < log_r` is equivelent to `u < r` but works in log-space!

## Question A: Visualising the Results

### Monte Carlo Estimates

Computing the sample mean and standard deviation (lines 48-49) was straightforward once I had the samples:
```python
sample_mean = np.mean(samples)
sample_std = np.std(samples, ddof=1)
```

The `ddof=1` parameter was something I had to look up - it gives the unbiased sample standard deviation. Without it, the estimates were slightly off and again took quite a while to figure it out and only due to the help of stack overflow answers.

### Creating the Visualizaton

The plot generation (lines 54-78) required combining three different representations:
1: A histogram of the samples
2: A kernel density estimte (KDE)
3: The true target distribtuion

The histogram code (lines 58-59):
```python
plt.hist(samples, bins=50, density=True, alpha=0.6, color='blue',
         label='Histogram', edgecolor='black')
```

The `density=True` paramter was critical - without it, the histogram wouldnt be on the same scale as the probabilty density function. I initialy forgot this and spent the entire afternoone wondering why my histogram was way too tall! So frustating.

The resulting plot (`metropolis-results.png`) shows that:
- The blue histogram represents the empirical distribution of our samples
- The red KDE line smooths out the histogram, showing the estimted density
- The green dashed line is the true N(0,1) f(x) distribtuion we're trying to sample from

The close alignment of all three curves validates that our Metropolis-Hastings implementation is working corectly - we're succesfully sampling from the target distribtuion! Finally something worked.

## Question B: Gelman-Rubin Diagnostic - The Real Challange

### Understanding Multiple Chains

The Gelman-Rubin diagnostic was conceptualy much harder. The idea of running multiple chains with diferent starting points and comparing their convergance was not intuative at first. Why do we even need multiple chains? What does "convergance" even mean in this context? I was pretty confused about this whole thing.

After reading the theory multiple times (and watching some youtube videos and promting LLM's), I understood: if the chains have converged to the same distribution, they should have similar means and variances regardless of where they started. This is what R-hat measures aparently.

### Implementing the R-hat Calculation

The R-hat formula was the most mathematically dense part and honestly gave me a lingering headache.

R̂ = sqrt((B + W) / W)

where:
- W = within-chain varience (average of individual chain variances)
- B = between-chain varience (variance of chain means)

The implementation (lines 106-126) required careful atention to the formulas:
```python
def calc_rhat(chains):
    J = len(chains)  # number of chains
    N = len(chains[0])  # length of each chain
    
    M_j = np.array([np.mean(chain) for chain in chains])  # chain means
    V_j = np.array([np.var(chain, ddof=1) for chain in chains])  # chain variances
    
    W = np.mean(V_j)  # within-chain varience
    M = np.mean(M_j)  # overall mean
    B = N / (J - 1) * np.sum((M_j - M)**2)  # between-chain varience
    
    R_hat = np.sqrt((B + W) / W)
    
    return R_hat
```

I made several mistakes here that took days to debug:
1. Initialy didn't reference the correct chain[0] element
2. Got confused about wether to use `N` or `N-1` in the B formula (its N!)

### The Burn-in Period Problem

One major issue I encounterd was that with very small step sizes (s=0.001), the chains would start far from the target distribtuion and take forever to converge. This is why I added a burn-in period (line 136):
```python
burnin = 500  # throw away first 500 samples
```

The implementation (lines 147-149):
```python
full_chain = run_chain(x0=init_vals[j], N=N_b+burnin, s=s_b, seed=j*100)
chain = full_chain[burnin:]  # discard burn-in
```

This was curcial! Without burn-in, the R-hat values were completly wrong because the chains hadn't reached the stationary distribtuion yet. Took me a couple of tinkering to find the most optimal cut of point.

### Choosing Starting Values

Another subtle issue: I initially used starting values like [-10, -5, 5, 10] which were too far apart. With small step sizes, the chains would never converge! I changed to closer values (line 141):
```python
init_vals = [-0.5, -0.2, 0.2, 0.5]
```

This made a huge difference in convergence behavior. I didn't know starting values mattered so much?

### Plotting R-hat vs Step Size

The most computationaly intensive part was computing R-hat for 50 different step sizes (lines 165-180). This required running 4 chains for each step size, which meant 200 total chains! My laptop was not happy about this on the first attempt missing some key data.

```python
s_vals = np.linspace(0.001, 1, 50)
rhat_vals = []

for idx, s_val in enumerate(s_vals):
    chains_s = []
    for j in range(J_b):
        full_chain = run_chain(x0=init_vals[j], N=N_b+burnin, s=s_val, seed=j*100)
        chain = full_chain[burnin:]
        chains_s.append(chain)
    
    rhat_s = calc_rhat(chains_s)
    rhat_vals.append(rhat_s)
```

The resulting plot (`gelman-rubin-diagnostic.png`) reveals some facinating insights:
- The red horizontal line at 1.05 is the convergance threshold
- The green line at 1.0 represents perfect convergance
- The red dot marks our specific case (s=0.001)
- The curve shows that R-hat increases with larger step sizes

### Interpreting the Results

The plot shows that:
1. Very small step sizes (s ≈ 0.001) give excellent convergance (R-hat ≈ 1.0)
2. As step size increases, R-hat initially stays low
3. Around s ≈ 0.5-7, R-hat starts increasing significently
4. Large step sizes lead to poor convergance (R-hat > 1.05)

This makes intuative sense, but not for me initially. Small steps has too much data and renders/plots slowly, while large steps might jump around too much and miss important data.

## Visualization Success in Part 1

One unexpected bright spot in this project was how clear and readable the visualizations turned out in Part 1, especially compared to Part 2. The Metropolis-Hastings results plot successfully layered a histogram, KDE curve, and true distribtuion on a single graph without any visual clutter. The Gelman-Rubin diagnostic plot was equaly successful, with reference lines at the convergance thresholds and a highlighted point for our specific case making interpretaton immediate and intuative. Unlike Part 2, where multiple categorical variables, dozens of regression coefficients, and trends across five years created unavoidably cluttered visualizatoins with tiny fonts and legends placed outside the plot area, Part 1's simpler data structure - univariate samples and a single convergance metric, naturaly lent itself to clean visualizatons. Maybe by postponing part 1 after part 2, my plotting skills had improved drastically, or maybe the data was simply more amenible to clean visualization. Either way, this was a pleasent supprise and a reminder that thoughtful data visualization is as much about the data and the question as it is about the plotting code itself.

![Metropolis-Hastings Results](PY/metropolis-results.png)
*Figure 1: Histogram, KDE, and true distribtuion showing succesful sampling from N(0,1)*

![Gelman-Rubin Diagnostic](PY/gelman-rubin-diagnostic.png)
*Figure 2: R-hat convergance diagonstic across diferent step sizes*

## Conclusion

What seemed like a simple algorithm on paper turned into a complex implementaton challange. The main dificulties were understanding how to compute acceptence ratios without numerial errors, iplementing the Gelman-Rubin diagonstic corectly. Choosing apropriate parametrs shuch as burn-ins, starting values and step sizes.

The final implementaton successfully samples from the target distribtution (as shown in `metropolis-results.png`) and provides robust convergance diagonstics (as shown in `gelman-rubin-diagnostic.png`). However, getting there required numerous iteratons, debuging sessions, and a deep dive into both the mathmatical theory and practical implementaton details far beyond my current skills. Honestly way harder than I thought it would be.

The experiance taught me that statistical algoritms require careful atention to numerial stability, paramter tuning, and validaton, clearly nothing for the faint hearted and definately not something you can rush through the night before the deadline.

