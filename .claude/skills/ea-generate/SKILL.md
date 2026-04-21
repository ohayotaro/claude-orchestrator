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

**Assess scope**: If the EA requires multiple include files (shared library, custom indicators, utility modules), transition to `/team-implement` with the design from Step 2 as input, assigning `ea-developer` to each MQL5 file.

For single-file EAs, generate MQL5 code in `mql5/experts/`:
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

### Step 5: Parity Verification
Verify that the generated MQL5 logic matches the source Python strategy:
- Compare signal generation conditions side by side
- Verify parameter mapping (Python defaults ↔ MQL5 input parameters)
- Check risk controls are equivalent (SL/TP, lot sizing, emergency stop)

For full code quality review (security, performance, correctness), run `/team-review`.

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
