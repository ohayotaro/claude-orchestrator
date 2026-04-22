---
name: sector-analysis
description: Analyze sector performance, rotation patterns, and cross-sector correlations. Supports sector rotation strategy design and portfolio sector allocation.
agent: quant-analyst
allowed-tools: "Bash(python *) Bash(uv *) Bash(codex *) Bash(gemini *) Read Write Edit Glob Grep"
---

# Sector Analysis & Rotation

Analyze sector dynamics for rotation strategies and portfolio allocation.

## Workflow

### Step 1: Define Universe
Ask the user:
1. Market (Japan: TOPIX sectors, US: GICS sectors, global)
2. Sector classification (GICS, TOPIX-17, custom)
3. Analysis timeframe (short-term momentum, long-term cycle)
4. Benchmark index

### Step 2: Sector Data Collection
Using data-engineer subagent:
- Sector index/ETF price data
- Individual stock data per sector
- Macro indicators (yield curve, PMI, CPI, monetary policy)
- Fund flow data (if available)

### Step 3: Performance Analysis
Calculate per sector:
- Absolute return (1M, 3M, 6M, 12M)
- Relative return vs benchmark
- Momentum score (rate of change, acceleration)
- Volatility and risk-adjusted return (sector Sharpe)
- Breadth (% of stocks above moving average)

### Step 4: Correlation Analysis
- Sector-to-sector correlation matrix
- Rolling correlation stability
- Identify diversification opportunities (low-correlation pairs)
- Detect regime changes in correlation structure

### Step 5: Rotation Signal Generation
Methods:
- **Momentum rotation**: Overweight top-N sectors by 6M/12M return
- **Mean reversion**: Overweight lagging sectors (contrarian)
- **Macro-linked**: Map economic cycle to sector preferences
  - Early cycle: Technology, Consumer Discretionary
  - Mid cycle: Industrials, Materials
  - Late cycle: Energy, Healthcare
  - Recession: Utilities, Consumer Staples
- **Relative strength**: Rank sectors by RS vs benchmark

### Step 6: Codex Review
```bash
codex exec "Review this sector rotation analysis:
{sector_rankings_and_signals}

Evaluate:
1. Is the rotation signal consistent with macro environment?
2. Are there concentration risks in top sectors?
3. Historical persistence of sector momentum (regime dependency)?
4. Transaction cost impact of rotation frequency?"
```

### Step 7: Gemini Visual Analysis (Optional)
For sector heatmaps and performance charts:
```bash
gemini -p "Analyze this sector performance heatmap.
Identify: strongest/weakest sectors, rotation patterns, divergences." -f sector_heatmap.png
```

### Step 8: Output
- Sector ranking table with scores
- Recommended allocation weights
- Rotation signal (overweight/underweight per sector)
- Macro context summary
- Integration notes for `/strategy-design`
