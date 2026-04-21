---
name: risk-report
description: Generate portfolio risk assessment reports with VaR/CVaR calculations, stress testing, and Codex model validation.
agent: quant-analyst
allowed-tools: "Bash(python *) Bash(codex *) Read Write Edit Glob Grep"
---

# Risk Report Generator

Comprehensive portfolio risk evaluation.

## Workflow

### Step 1: Portfolio Information
Gather current portfolio state:
- Open positions (instrument, direction, size, entry price)
- Account balance and equity
- Active strategies and their parameters

### Step 2: VaR/CVaR Calculation
Using the **quant-analyst** subagent:
- **Historical VaR**: Based on historical returns distribution
- **Parametric VaR**: Assuming normal/t-distribution
- **Monte Carlo VaR**: Simulated portfolio paths (10,000+ scenarios)
- **CVaR** (Expected Shortfall): Average loss beyond VaR

Confidence levels: Configurable (default: 95%, 99%)
Horizons: Configurable (default: 1-day, 1-week, 1-month)

### Step 3: Stress Testing
Simulate portfolio under extreme scenarios:
- Flash crash (-10% in 1 hour)
- Black swan event (-30% in 1 week)
- Correlation breakdown (safe-haven failure)
- Liquidity crisis (10x spread widening)
- Interest rate shock (for FX positions)

### Step 4: Correlation Analysis
- Current correlation matrix for all positions
- Rolling correlation stability
- Tail correlation (correlations during extreme moves)
- Diversification ratio

### Step 5: Codex Model Validation
```bash
codex -a on-request "Validate risk model:
- VaR (95%, 1d): {value}
- CVaR (95%, 1d): {value}
- Max portfolio drawdown potential: {value}
- Correlation assumptions: {matrix}

Check:
1. Are distributional assumptions reasonable?
2. Are tail risks adequately captured?
3. Is the stress test scenario set comprehensive?
4. Are there hidden concentration risks?"
```

### Step 6: Report Output
Generate report in `reports/`:
- Executive summary (3-line risk assessment)
- VaR/CVaR table by confidence level and horizon
- Stress test results table
- Correlation heatmap
- Risk decomposition by strategy/instrument
- Recommendations for risk reduction
