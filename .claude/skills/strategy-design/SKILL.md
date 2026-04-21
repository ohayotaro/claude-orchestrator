---
name: strategy-design
description: Design new trading strategies with parallel Researcher/Strategist analysis, Codex algorithm design review, and complete strategy specification.
allowed-tools: "Bash(python *) Bash(codex *) Read Write Edit Glob Grep"
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

### Step 2: Parallel Research (Agent Teams)
Launch two subagents in parallel:

**Researcher** (general-purpose):
- Search for similar strategies in academic literature
- Analyze existing strategies in `src/strategies/`
- Review relevant market microstructure
- Identify potential pitfalls

**Strategist** (strategist):
- Design signal generation logic
- Define entry/exit rules
- Specify position sizing approach
- Outline risk parameters

### Step 3: Synthesis
Integrate findings from both agents:
- Merge research insights with strategy design
- Resolve conflicts between theoretical and practical considerations
- Define complete strategy specification

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

### Step 5: Strategy File Generation
Create strategy file in `src/strategies/`:
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
