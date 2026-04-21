# Codex Handoff Playbook

Templates for delegating tasks to Codex CLI.

## 1. Strategy Design Review

```bash
codex --approval-mode suggest "
You are reviewing a trading strategy design for a financial trading system.

## Strategy
{paste strategy description}

## Review Checklist
1. Statistical edge validity — does the stated edge have theoretical/empirical support?
2. Overfitting risk — parameter count, IS/OOS gap, data snooping potential
3. Market regime dependency — will this fail in trending/ranging/volatile conditions?
4. Implementation feasibility — can this be implemented efficiently in Python and MQL5?
5. Risk controls — are stop loss, position sizing, and max drawdown properly defined?

Provide your assessment with confidence levels (High/Medium/Low) for each item.
"
```

## 2. Backtest Statistical Validation

```bash
codex --approval-mode suggest "
Validate the statistical significance of these backtest results:

## Results
{paste backtest metrics}

## Validation Tasks
1. Calculate p-value for the Sharpe ratio (H0: Sharpe = 0)
2. Bootstrap 95% confidence interval for annual return
3. Run White's Reality Check for data snooping bias
4. Compare IS vs OOS performance gap
5. Assess parameter stability across sub-periods

Flag any signs of overfitting or look-ahead bias.
"
```

## 3. MQL5 EA Code Review

```bash
codex --approval-mode suggest "
Review this MQL5 Expert Advisor code:

## Code
{paste EA code}

## Review Focus
1. Order management correctness — CTrade usage, OrderSend validation
2. Memory leak prevention — ArrayFree, indicator handle release
3. Error handling completeness — GetLastError after every operation
4. Slippage and spread handling — deviation parameters, spread checks
5. Magic number management — uniqueness, filtering
6. Risk control implementation — SL/TP, lot sizing, emergency stop

Provide specific line-by-line feedback.
"
```

## 4. Error Root Cause Analysis

```bash
codex --full-auto "
Analyze and fix this error in a financial trading system:

## Error
{paste error/traceback}

## Context
- File: {file path}
- Function: {function name}
- Last working state: {description}

Identify root cause, propose fix, and suggest a regression test.
"
```

## 5. Algorithm Optimization

```bash
codex --approval-mode suggest "
Optimize this trading algorithm for performance:

## Current Implementation
{paste code}

## Requirements
- Must handle 1M+ rows of OHLCV data
- Must complete backtest in under 60 seconds
- Must maintain numerical precision for financial calculations
- Must be vectorized where possible (numpy/pandas/vectorbt)

Propose optimizations with expected speedup estimates.
"
```

## 6. Risk Model Design

```bash
codex --approval-mode suggest "
Design a risk management model for this trading system:

## Portfolio
{describe portfolio composition}

## Requirements
1. VaR calculation (Historical, Parametric, Monte Carlo)
2. CVaR (Expected Shortfall)
3. Position sizing (Kelly criterion variant)
4. Correlation-adjusted risk
5. Stress testing framework

Provide mathematical formulation and Python implementation.
"
```
