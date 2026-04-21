---
name: earnings-calendar
description: Manage earnings calendar, dividend events, and corporate actions. Supports event-driven strategy design and pre/post-earnings position management.
agent: data-engineer
allowed-tools: "Bash(python *) Bash(uv *) Read Write Edit Glob Grep"
---

# Earnings Calendar & Corporate Events

Manage corporate events that impact trading decisions.

## Workflow

### Step 1: Event Data Acquisition
Fetch event calendar data:
- **Earnings dates**: Scheduled earnings announcement dates
- **Dividend dates**: Ex-date, record date, payment date, amount
- **Stock splits**: Split ratio, effective date
- **Other corporate actions**: Mergers, spinoffs, delistings

Data sources (configurable):
- yfinance `calendar` / `earnings_dates`
- Exchange announcement feeds
- Commercial providers as configured

### Step 2: Calendar Construction
Build unified event calendar:
```
Date       | Symbol | Event Type    | Details
2026-04-25 | AAPL   | Earnings      | Q2 FY2026, after-market
2026-04-28 | MSFT   | Ex-Dividend   | $0.75/share
2026-05-01 | TSLA   | Stock Split   | 5:1
```

### Step 3: Earnings Analysis
For earnings-driven strategies:
- **Pre-earnings**: Historical volatility expansion pattern
- **Earnings surprise**: Actual vs consensus EPS
- **Post-earnings drift**: Price momentum after surprise direction
- **Implied volatility**: Options-implied move vs historical average

### Step 4: Dividend Management
- Track ex-dates for portfolio positions
- Calculate dividend-adjusted returns
- Flag positions at risk of ex-date gap
- Model dividend reinvestment impact

### Step 5: Position Rules Around Events
Define automated rules:
```
Before earnings (configurable buffer, default: 1 day):
  - Option A: Reduce position to N% (risk reduction)
  - Option B: Hold (earnings drift strategy)
  - Option C: Close entirely (no event risk)

Before ex-dividend date:
  - Track dividend capture opportunity
  - Adjust stop-loss for expected gap-down
```

### Step 6: Integration with Strategy
- Export event calendar as feature for ML models
- Add earnings/dividend flags to backtest data
- Adjust backtest P&L for dividends received
- Prevent false signals from corporate action price gaps
