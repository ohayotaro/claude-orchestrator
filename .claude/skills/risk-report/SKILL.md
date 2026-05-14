---
name: risk-report
description: Generate portfolio risk assessment reports with VaR/CVaR calculations, stress testing, and Codex model validation. Supports per-strategy, risk-group, and account-scope aggregation.
agent: quant-analyst
allowed-tools: "Bash(python *) Bash(codex *) Read Write Edit Glob Grep"
---

# Risk Report Generator

Comprehensive portfolio risk evaluation at per-strategy, risk-group, and account scope.

## Precondition: Invocation Modes

This skill operates in three modes determined by the invocation arguments:

| Invocation | Scope | Description |
|---|---|---|
| `risk-report strategy {strategy_id}` | Per-strategy | Report for a single strategy. This is the mode that satisfies the `/risk-report` precondition required for `live` promotion (`multi-strategy.md` section 4). |
| `risk-report group {risk_group}` | Risk-group | Aggregate across all strategies sharing the given `risk_group` in `config/registry.toml`. |
| `risk-report account {account_scope}` | Account | Aggregate across all strategies sharing the given `account_scope` in `config/registry.toml`. |

If invoked without arguments, ask the user which mode and identifier to use.

In every mode, the skill MUST:
1. Read `config/registry.toml` to resolve strategy metadata and filter by the requested scope.
2. Refuse to operate on a `strategy_id` not present in the registry (hint the user to run `/strategy-register`).
3. Refuse to operate on a `risk_group` or `account_scope` that matches zero strategies in the registry.
4. Tag all generated artifacts with `strategy_id` (per-strategy) or `risk_group` / `account_scope` (aggregated), plus `logic_version` where applicable.

### Report Output Paths

| Mode | Output path |
|---|---|
| Per-strategy | `reports/strategies/{strategy_id}/risk_{timestamp}.md` |
| Risk-group | `reports/risk_groups/{risk_group}_{timestamp}.md` |
| Account | `reports/accounts/{account_scope}_{timestamp}.md` |

Create the output directory if it does not exist.

## Workflow

### Step 1: Portfolio Information
Gather current portfolio state, scoped to the invocation mode:

**Per-strategy mode** (`strategy_id`):
- Open positions for this strategy (instrument, direction, size, entry price)
- Account balance and equity for this strategy's `account_scope`
- Strategy parameters from `config/strategies/{strategy_id}.toml`

**Group mode** (`risk_group`):
- Read `config/registry.toml` and select all strategies where `risk_group` matches
- For each member strategy, gather: `strategy_id`, `state`, `enabled`, open positions, daily PnL
- Account balance and equity for the accounts referenced by the group

**Account mode** (`account_scope`):
- Read `config/registry.toml` and select all strategies where `account_scope` matches
- For each member strategy, gather the same data as group mode
- Account-level balance, equity, and margin information

### Step 2: VaR/CVaR Calculation
Using the **quant-analyst** subagent:
- **Historical VaR**: Based on historical returns distribution
- **Parametric VaR**: Assuming normal/t-distribution
- **Monte Carlo VaR**: Simulated portfolio paths (10,000+ scenarios)
- **CVaR** (Expected Shortfall): Average loss beyond VaR

Confidence levels: Configurable (default: 95%, 99%)
Horizons: Configurable (default: 1-day, 1-week, 1-month)

In group/account mode, calculate VaR/CVaR at both the per-strategy level and the aggregate level. The aggregate is NOT the sum of per-strategy VaR (diversification effects apply).

### Step 3: Stress Testing
Simulate portfolio under extreme scenarios:
- Flash crash (-10% in 1 hour)
- Black swan event (-30% in 1 week)
- Correlation breakdown (safe-haven failure)
- Liquidity crisis (10x spread widening)
- Interest rate shock (for FX positions)

In group/account mode, stress tests run against the combined portfolio of all member strategies.

### Step 4: Correlation Analysis
- Current correlation matrix for all positions
- Rolling correlation stability
- Tail correlation (correlations during extreme moves)
- Diversification ratio

In group/account mode, include cross-strategy position correlation (positions from different strategies on the same or correlated instruments).

### Step 5: Codex Model Validation
Pass the invocation scope to Codex so the review is properly scoped:

**Per-strategy mode:**
```bash
codex exec "Validate risk model for strategy {strategy_id} (logic_version {logic_version}):
- VaR (95%, 1d): {value}
- CVaR (95%, 1d): {value}
- Max strategy drawdown potential: {value}
- Correlation assumptions: {matrix}

Check:
1. Are distributional assumptions reasonable for this strategy?
2. Are tail risks adequately captured?
3. Is the stress test scenario set comprehensive?
4. Are there hidden concentration risks within this strategy?"
```

**Group/account mode:**
```bash
codex exec "Validate aggregated risk model for {risk_group|account_scope}:
- Strategies included: {list of strategy_id with state and enabled flag}
- Aggregate VaR (95%, 1d): {value}
- Aggregate CVaR (95%, 1d): {value}
- Group drawdown vs high-water mark: {value}
- Net exposure: {value}, Gross exposure: {value}
- Margin utilization: {value} (account mode only)

Check:
1. Are cross-strategy correlations adequately modeled?
2. Is the net exposure after cross-strategy netting reasonable?
3. Are there hidden concentration risks across strategies (same symbol, same sector)?
4. Do the soft/hard cap thresholds from risk-management.md align with the observed risk?"
```

### Step 6: Report Output
Generate report at the path defined in "Report Output Paths" above.

**Per-strategy report contents:**
- Executive summary (3-line risk assessment)
- VaR/CVaR table by confidence level and horizon
- Stress test results table
- Correlation heatmap
- Risk decomposition by instrument
- Recommendations for risk reduction

**Aggregated report contents (group/account mode) -- in addition to the above:**
- List of contributing strategies with `strategy_id`, `state`, `enabled` flag
- Per-strategy contribution to total exposure, daily PnL, drawdown
- Group-level metrics: net exposure, gross exposure, total daily PnL, group drawdown vs. high-water mark, total open position count
- Margin utilization (account-scoped mode only)
- Concentration analysis: per-symbol and per-asset exposure across strategies, flagging any symbol held by multiple strategies
- Recommendations scoped to the group/account (e.g., reduce correlated exposure across strategies)
