---
name: market-analysis
description: Analyze current market conditions with multi-timeframe analysis, Gemini chart pattern recognition, and cross-market correlation analysis.
allowed-tools: "Bash(python *) Bash(gemini *) Read Write Edit Glob Grep"
---

# Market Analysis

Comprehensive analysis of current market conditions.

## Workflow

### Step 1: Data Collection
- Fetch latest data for target instruments
- Multiple timeframes (1h, 4h, 1d, 1w)
- Related instruments for correlation analysis

### Step 2: Technical Indicator Calculation
Calculate via Python:
- Trend: SMA, EMA, MACD, ADX
- Momentum: RSI, Stochastic, CCI
- Volatility: ATR, Bollinger Bands, Keltner Channels
- Volume: OBV, VWAP (where available)

### Step 3: Multi-Timeframe Analysis
- Higher TF: Determine overall trend direction
- Middle TF: Identify trading range and key levels
- Lower TF: Find entry/exit timing signals

### Step 4: Chart Generation
Generate charts with matplotlib/plotly:
- Candlestick with key indicators
- Volume profile
- Multi-timeframe dashboard

### Step 5: Gemini Chart Analysis
Send generated charts to Gemini for pattern recognition:
```bash
gemini -p "Analyze this price chart for:
1. Key support/resistance levels with price values
2. Chart patterns (H&S, triangles, wedges, flags)
3. Trend strength and direction assessment
4. Volume profile analysis
5. Potential reversal or continuation signals
Provide confidence level (High/Medium/Low) for each finding." -f chart.png
```

### Step 6: Cross-Market Correlation
- Analyze correlation between related instruments
- Detect divergences (e.g., BTC vs ETH, USD/JPY vs Nikkei)
- Identify leading/lagging relationships

### Step 7: Report Generation
Output structured analysis report:
- Market regime classification (trending/ranging/volatile)
- Key levels and zones
- Bias (bullish/bearish/neutral) with confidence
- Risk factors and scenarios to watch
