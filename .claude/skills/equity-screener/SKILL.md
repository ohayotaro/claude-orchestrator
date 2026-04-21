---
name: equity-screener
description: Screen stocks using fundamental and technical criteria. Covers valuation metrics, growth analysis, sector filtering, and financial statement data.
agent: quant-analyst
allowed-tools: "Bash(python *) Bash(uv *) Bash(codex *) Read Write Edit Glob Grep"
---

# Equity Screener

Screen and filter stocks based on fundamental, technical, and quantitative criteria.

## Workflow

### Step 1: Define Screening Criteria
Ask the user:
1. Universe (market/exchange: TSE, NYSE, NASDAQ, global)
2. Screening approach (value, growth, momentum, dividend, quality, or custom)
3. Key metrics to filter on
4. Sector/industry constraints (include/exclude)

### Step 2: Data Acquisition
Fetch fundamental data via data-engineer subagent:
- **Price data**: OHLCV (daily, adjusted for splits/dividends)
- **Financial statements**: Income statement, balance sheet, cash flow
- **Valuation metrics**: P/E, P/B, EV/EBITDA, dividend yield
- **Growth metrics**: Revenue growth, EPS growth, earnings revisions
- **Quality metrics**: ROE, ROA, debt/equity, free cash flow yield

Data sources (configurable per project):
- Free: yfinance, EDINET (Japan), SEC EDGAR (US)
- Commercial: Bloomberg, Refinitiv, FactSet, as configured

### Step 3: Build Screening Filters
Define quantitative filters:

**Value Screen Example:**
```
P/E < sector median
P/B < 1.5
Dividend yield > 2%
Debt/Equity < 1.0
```

**Growth Screen Example:**
```
Revenue growth (YoY) > 15%
EPS growth (YoY) > 20%
ROE > 15%
Earnings revision (3-month) > 0
```

**Momentum Screen Example:**
```
6-month return > market return
12-month return in top 20% of universe
Relative strength > 1.0
Volume trend increasing
```

### Step 4: Ranking and Scoring
- Assign weights to each criterion
- Composite score calculation
- Rank stocks within universe
- Flag outliers for manual review

### Step 5: Codex Valuation Review
For top candidates, delegate deep analysis:
```bash
codex -a on-request "Review this stock screening result:
{top_candidates_with_metrics}

Evaluate:
1. Are the valuation metrics consistent (no data quality issues)?
2. Any red flags in financial statements (accounting anomalies)?
3. Sector concentration risk in the filtered set?
4. Forward-looking risks not captured by historical data?"
```

### Step 6: Output
- Screened stock list with scores and key metrics
- Sector distribution summary
- Comparison to benchmark universe
- Candidates for further strategy design via `/strategy-design`
