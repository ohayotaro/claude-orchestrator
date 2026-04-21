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

### Step 7: Hyperparameter Optimization (HPO Framework)
For large search spaces, use an HPO framework (Optuna recommended):
```python
import optuna

study = optuna.create_study(
    study_name="{strategy}_{timestamp}",
    direction="maximize",  # maximize Sharpe
    storage="sqlite:///reports/optuna.db",  # persistent storage
    pruner=optuna.pruners.MedianPruner(n_warmup_steps=20),
)
study.optimize(objective, n_trials=200, show_progress_bar=True)
```

- Use TPE sampler (default) for efficient Bayesian search
- Enable pruning to skip unpromising trials early
- Store results in SQLite for cross-session persistence
- Visualize: `optuna.visualization.plot_param_importances(study)`

### Step 8: Ablation Analysis
- Remove each component/parameter → measure impact on Sharpe
- Identify load-bearing vs decorative parameters
- Prefer minimal parameter sets (fewer params = less overfitting)

### Step 9: Generate Report
Save optimization results to `reports/`:
- Parameter heatmaps
- Walk-forward equity curves
- Monte Carlo distribution charts
- Final parameter set with confidence intervals
- Optuna study summary (best trial, param importances)
- Ablation results table
