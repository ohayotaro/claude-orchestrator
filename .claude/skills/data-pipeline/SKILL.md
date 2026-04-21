---
name: data-pipeline
description: Build and manage market data acquisition, normalization, and storage pipelines for any exchange or data provider.
agent: data-engineer
allowed-tools: "Bash(python *) Bash(uv *) Read Write Edit Glob Grep"
---

# Data Pipeline Builder

Build market data fetching, cleaning, and storage pipelines.

## Workflow

### Step 1: Requirements Gathering
Ask the user:
1. Target market and instruments (e.g., BTC/USDT, EUR/USD, ES futures)
2. Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
3. Date range (start, end)
4. Data source (select from project's configured sources, or specify custom API)

### Step 2: Design Data Schema
Using the **data-engineer** subagent, design:
- OHLCV schema (timestamp, open, high, low, close, volume)
- Additional fields (funding rate, open interest, if applicable)
- Metadata schema (source, instrument, timeframe, fetch date)

### Step 3: Implement Fetcher
Create data fetching module in `src/data/`:
- API client with rate limiting and retry logic
- Pagination for large date ranges
- Error handling for API downtime

### Step 4: Implement Cleaner
Create data cleaning module:
- Timezone normalization to UTC
- Missing value detection and handling
- Outlier detection (price spikes, volume anomalies)
- OHLCV consistency checks (high >= open, close, low)

### Step 5: Storage
- Save to Parquet format in `data/` directory
- Generate metadata JSON alongside each data file
- Implement deduplication for re-fetches

### Step 6: Codex Review (if complex)
For large data processing logic, delegate design review to Codex:
```bash
codex --approval-mode suggest "Review data pipeline design: {context}"
```

### Step 7: Validation
- Run data quality checks
- Verify row counts match expected candle count
- Compare sample data against exchange UI
