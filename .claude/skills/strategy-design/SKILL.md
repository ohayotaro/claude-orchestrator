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
codex -a on-request "Review this trading strategy design:
{strategy_specification}

Evaluate:
1. Statistical edge validity
2. Overfitting risk (parameter count, complexity)
3. Market regime dependency
4. Implementation feasibility in Python and MQL5
5. Risk control completeness"
```

### Step 5: Strategy Implementation

**Assess scope**: If the strategy requires multiple independent modules (signal generator, risk module, data adapter), transition to `/team-implement` with the design from Step 3-4 as input.

For single-module strategies, create strategy file in `src/strategies/`:
- Inherit from base strategy class
- Implement signal generation
- Implement entry/exit logic
- Define all parameters with ranges for optimization
- Include docstring with edge rationale

### Step 6: Parameter Specification
Generate parameter document:
- Parameter name, type, default, range
- Sensitivity expectations
- Correlation between parameters

### Step 7: Test Skeleton
Create corresponding test file in `tests/test_strategies/`
