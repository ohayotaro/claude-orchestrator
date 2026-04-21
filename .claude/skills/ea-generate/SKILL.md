---
name: ea-generate
description: Convert Python trading strategies to MQL5 Expert Advisors with Codex code review, order management, and risk controls.
agent: ea-developer
allowed-tools: "Bash(python *) Bash(codex *) Read Write Edit Glob Grep"
---

# MQL5 EA Generator

Convert Python strategies to MetaTrader 5 Expert Advisors.

## Workflow

### Step 1: Source Strategy Analysis
- Read target Python strategy from `src/strategies/`
- Extract signal logic, entry/exit rules, parameters
- Identify indicators and their MQL5 equivalents

### Step 2: EA Architecture Design
Using the **ea-developer** subagent, design:
- OnInit: Indicator handle creation, input parameter validation
- OnTick: Signal generation, order management loop
- OnDeinit: Handle release, cleanup
- Input parameters mapping from Python strategy
- Magic number assignment

### Step 3: Implement Core Logic
Generate MQL5 code in `mql5/experts/`:
- Signal generation matching Python logic exactly
- CTrade order management (market orders, pending orders)
- Position tracking with magic number filtering

### Step 4: Implement Risk Controls (Mandatory)
- Stop loss calculation and setting
- Take profit calculation and setting
- Lot size calculation (fixed or % of balance)
- Max spread check before entry
- Max concurrent positions check
- Daily loss limit check
- Emergency stop mechanism

### Step 5: Codex Code Review
```bash
codex -a on-request "Review this MQL5 Expert Advisor:
{ea_code}

Check:
1. Order management correctness (CTrade, error handling)
2. Memory leak prevention (indicator handles, arrays)
3. GetLastError() usage after every trade operation
4. Slippage and spread handling
5. Magic number management
6. Risk controls completeness (SL/TP, lot sizing, emergency stop)
7. Parity with original Python strategy logic"
```

### Step 6: Test Configuration
Generate MetaTrader Strategy Tester config:
- Symbol, period, date range
- Spread model (every tick vs 1-minute OHLC)
- Initial deposit and leverage
- Optimization parameters (if applicable)

### Step 7: Output
- EA file: `mql5/experts/{strategy_name}_EA.mq5`
- Include file (if needed): `mql5/include/{strategy_name}_common.mqh`
- Test config documentation
- Deployment checklist (broker requirements, VPS setup)
