---
name: optimize
description: Strategy parameter optimization with walk-forward analysis, overfitting detection, and Monte Carlo robustness testing.
agent: quant-analyst
allowed-tools: "Bash(python *) Bash(codex *) Read Write Edit Glob Grep"
---

# Parameter Optimization

Optimize strategy parameters with rigorous overfitting prevention.

## Workflow

### Step 1: Define Optimization Scope
- Identify target strategy and parameters
- Set parameter ranges and step sizes
- Choose objective function (Sharpe, Calmar, custom)

### Step 2: Walk-Forward Analysis
Using the **quant-analyst** subagent:
- Split data into rolling windows (e.g., 12-month IS, 3-month OOS)
- Optimize on IS, validate on OOS for each window
- Aggregate OOS results for final performance estimate

### Step 3: Out-of-Sample Testing
- Reserve final 20-30% of data as holdout
- Run strategy with optimized parameters on holdout
- Compare IS vs OOS performance

### Step 4: Overfitting Detection via Codex
```bash
codex --approval-mode suggest "Evaluate overfitting risk:
- IS Sharpe: {is_sharpe}, OOS Sharpe: {oos_sharpe}
- Parameter count: {count}, Data points: {n}
- IS/OOS performance gap: {gap}%
Perform:
1. White's Reality Check
2. Parameter stability analysis (how much do optimal params change across windows?)
3. Combinatorially Symmetric Cross-Validation (CSCV) if applicable
4. Deflated Sharpe Ratio calculation"
```

### Step 5: Monte Carlo Simulation
- Randomize trade order (1000+ iterations)
- Bootstrap returns with replacement
- Calculate confidence intervals for key metrics
- Estimate probability of ruin

### Step 6: Select Final Parameters
- Choose parameters that are robust across windows
- Prefer parameters near the center of profitable regions (not edges)
- Document sensitivity analysis

### Step 7: Generate Report
Save optimization results to `reports/`:
- Parameter heatmaps
- Walk-forward equity curves
- Monte Carlo distribution charts
- Final parameter set with confidence intervals
