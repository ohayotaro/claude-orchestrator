---
name: strategy-design
description: Design new trading strategies with parallel Researcher/Strategist/Gemini analysis, Codex algorithm design review, and complete strategy specification.
allowed-tools: "Bash(python *) Bash(codex *) Bash(gemini *) Read Write Edit Glob Grep"
---

# Strategy Design

Design new trading strategies through structured collaborative analysis.

## Workflow

### Step 1: Requirements
Ask the user:
1. Target market and instruments
2. Trading style (scalping, day trading, swing, position)
3. Key hypothesis / edge idea
4. Risk tolerance (max drawdown, max risk per trade)

### Step 2: Parallel Research (Agent Teams + Gemini)
Launch three parallel tracks:

**Researcher** (general-purpose) — internal analysis:
- Analyze existing strategies in `src/strategies/` (what's already been tried, what worked)
- Review codebase for reusable components (indicators, signals, risk modules)
- Check backtest history in `reports/` for related strategy performance

**Gemini** — external knowledge acquisition:
```bash
gemini -p "Research trading strategies related to: {user's edge hypothesis}

Provide:
1. ACADEMIC EVIDENCE: Published papers or known studies supporting/refuting this edge
   (author, year, key finding, market tested on)
2. SIMILAR STRATEGIES: Known named strategies using this approach
   (name, mechanism, typical market, known weaknesses)
3. MARKET CONDITIONS: Under what regime does this edge tend to appear/disappear?
4. PRACTICAL CONSIDERATIONS: Typical transaction cost sensitivity, capacity limits,
   latency requirements
5. FAILURE MODES: Documented cases where this type of strategy failed and why

Cite sources where possible. State confidence level per finding."
```

If the user provides reference materials (PDFs, charts, screenshots):
```bash
gemini -p "Analyze this material for strategy design insights:
1. Key patterns or signals described
2. Performance claims and their conditions
3. Limitations or caveats mentioned
4. Applicable instruments and timeframes" -f {file}
```

**Strategist** (strategist) — design synthesis:
- Design signal generation logic based on the stated edge hypothesis
- Define entry/exit rules
- Specify position sizing approach
- Outline risk parameters

### Step 3: Synthesis
Integrate findings from all three tracks:
- **Gemini external research** → validate or challenge the edge hypothesis with evidence
- **Internal Researcher** → identify reusable components and avoid repeating past failures
- **Strategist design** → refine based on research findings
- Resolve conflicts between academic theory, practical codebase constraints, and strategy design
- If Gemini research contradicts the hypothesis, present evidence to the user before proceeding
- Define complete strategy specification with evidence-based rationale

### Step 4: Codex Design Review
Delegate to Codex for rigorous review:
```bash
codex exec "Review this trading strategy design:
{strategy_specification}

Evaluate:
1. Statistical edge validity
2. Overfitting risk (parameter count, complexity)
3. Market regime dependency
4. Implementation feasibility in Python and MQL5
5. Risk control completeness"
```

### Step 5: Register Strategy

Before implementation, mint a formal `strategy_id` via `/strategy-register register`. This ensures all downstream artifacts (code, tests, configs, reports) are scoped to a registry-managed identity from the start.

Invoke `/strategy-register register` with the values derived from Steps 1-4:
- `venue` — exchange or broker from the user's target market
- `market` — market segment (spot, swap, fx, cash, etc.)
- `logic_slug` — kebab-case name for the strategy logic (e.g., `mean-revert`, `ma-cross`)
- `symbol` — target instrument in exchange-native form
- `timeframe` — bar interval for the strategy
- `runtime` — `python` or `mql5`
- `account_scope` — project-defined account label (ask user if not clear)
- `risk_group` — project-defined risk bucket (ask user if not clear)
- `family_id` — defaults to `logic_slug` unless this is a variant of an existing family
- `logic_version` — `0.1.0` for a fresh design

The registration creates a `draft` entry in `config/registry.toml` and scaffolds per-strategy directories. Record the resulting `strategy_id` and `logic_version` — all subsequent design artifacts MUST reference them.

### Step 6: Strategy Implementation

**Assess scope**: If the strategy requires multiple independent modules (signal generator, risk module, data adapter), transition to `/team-implement` with the design from Step 3-4 as input, passing the `strategy_id` from Step 5.

For single-module strategies, create strategy file in `src/strategies/`:
- Inherit from base strategy class
- Implement signal generation
- Implement entry/exit logic
- Define all parameters with ranges for optimization
- Include docstring with edge rationale and `strategy_id`

### Step 7: Parameter Specification
Generate parameter document:
- Parameter name, type, default, range
- Sensitivity expectations
- Correlation between parameters

### Step 8: Test Skeleton
Create corresponding test file in `tests/test_strategies/`, scoped to the `strategy_id`.

### Step 9: Design Specification Output
Produce the final design specification document. The specification MUST include the following first-class fields at the top:

```
strategy_id:    {strategy_id from Step 5}
logic_version:  {logic_version from Step 5}
family_id:      {family_id}
venue:          {venue}
market:         {market}
symbol:         {symbol}
timeframe:      {timeframe}
runtime:        {runtime}
risk_group:     {risk_group}
state:          draft
```

Followed by: edge hypothesis, signal logic, entry/exit rules, position sizing, risk parameters, parameter specification, and Codex review findings.

Save the design specification to `reports/strategies/{strategy_id}/design_spec.md`.

## Downstream Skill Contract

Subsequent skills (`/backtest`, `/bot-develop`, `/ea-generate`, `/optimize`) MUST be invoked with the `strategy_id` produced by this skill. They will resolve all paths via `config/registry.toml` lookup. Do not pass ad-hoc identifiers or hardcoded paths.

If a strategy was designed without registration (legacy workflow), run `/strategy-register register` before proceeding to any downstream skill.
