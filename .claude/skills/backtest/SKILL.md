---
name: backtest
description: Execute trading strategy backtests with performance metrics, statistical validation via Codex, and optional Gemini chart interpretation.
agent: quant-analyst
allowed-tools: "Bash(python *) Bash(pytest *) Bash(codex *) Read Write Edit Glob Grep"
---

# Backtest Execution

Run backtests and generate comprehensive performance reports.

## Workflow

### Step 1: Strategy Identification
- Identify target strategy in `src/strategies/`
- Confirm parameters and data requirements
- Verify data availability in `data/`

### Step 2: Backtest Configuration
Using the **quant-analyst** subagent:
- Define IS/OOS split (minimum 70:30)
- Set transaction cost model (spread + commission + slippage)
- Configure initial capital and position sizing

### Step 3: Execute Backtest
Run via backtrader or vectorbt:
```bash
uv run python src/backtesting/runner.py --strategy {name} --data {path}
```

### Step 4: Performance Metrics
Calculate and report:
- **Returns**: Annual return, cumulative return, monthly returns
- **Risk**: Max Drawdown (amount, %, duration), Sharpe, Sortino, Calmar
- **Trades**: Win rate, Profit Factor, avg risk-reward ratio, max consecutive losses
- **Recovery**: Recovery Factor, time to recovery

### Step 5: Statistical Validation via Codex
Delegate to Codex CLI for rigorous validation:
```bash
codex --approval-mode suggest "Validate backtest results:
- Sharpe: {value}, Annual Return: {value}, Max DD: {value}
- Calculate p-value (H0: Sharpe=0)
- Bootstrap 95% CI for annual return
- Check for look-ahead bias indicators
- Compare IS vs OOS performance gap"
```

### Step 6: Generate Report
Save to `reports/`:
- HTML report with equity curve, drawdown chart, trade distribution
- CSV with trade-by-trade details
- JSON with summary metrics

### Step 7: Gemini Chart Interpretation (Optional)
If charts are generated, optionally send to Gemini:
```bash
gemini -p "Interpret this equity curve and drawdown chart. Identify concerning patterns." -f reports/equity_curve.png
```

### Step 8: Risk Threshold Check
Compare results against thresholds in `risk-management.md`:
- Warn if Sharpe < 1.0
- Warn if Max DD > 20%
- Warn if Win Rate < 40%
- Warn if Profit Factor < 1.5
