---
name: dashboard-develop
description: Build dashboards and visualization UIs for trading bots, backtest results, portfolio analytics, or research reports. Technology stack is selected based on use case.
allowed-tools: "Bash(python *) Bash(uv *) Bash(npm *) Bash(npx *) Bash(codex *) Read Write Edit Glob Grep"
---

# Dashboard & Visualization Development

Build UIs for monitoring, analysis, and reporting across any project use case.

## Workflow

### Step 1: Requirements
Ask the user:
1. **Use case** — what this dashboard is for:
   - (a) Live bot monitoring (positions, PnL, health, alerts)
   - (b) Backtest result viewer (equity curves, trade analysis, parameter heatmaps)
   - (c) Portfolio / risk dashboard (allocation, VaR, sector exposure)
   - (d) Research report viewer (IR analysis, earnings, sector comparison)
   - (e) Custom
2. **Audience** — who will use it (developer only, team, external stakeholders)
3. **Update frequency** — real-time (WebSocket), periodic (polling/cron), or static (on-demand generation)
4. **Deployment** — local only, internal hosting, public hosting, Docker service

### Step 2: Technology Selection

Choose stack based on use case. Do NOT default to a single stack — evaluate trade-offs:

| Use Case | Recommended Stack | Rationale |
|----------|------------------|-----------|
| Live bot monitoring | FastAPI + Vite SPA | Low latency, WebSocket support, customizable |
| Quick backtest viewer | Streamlit or Jupyter + Plotly | Rapid prototyping, interactive, Python-native |
| Portfolio dashboard | Streamlit or Dash | Data-heavy tables, charts from DataFrame |
| Research report viewer | Static HTML generation (Jinja2) | No server needed, easy to share/archive |
| Production team dashboard | FastAPI + Vite or Grafana | Robust, multi-user, alerting integration |

**Charting libraries** (select per need):
- **Plotly**: Interactive, wide chart types, Python + JS
- **Lightweight Charts** (TradingView): Candlestick-native, lightweight, JS only
- **Matplotlib**: Static export (PNG/PDF), publication-quality
- **Altair/Vega**: Declarative, good for statistical charts

### Step 3: Data Layer Design

Define how the dashboard gets its data:

**(a) Live data** (bot monitoring):
```
Bot process → structured log / SQLite / metrics endpoint
  → API server (FastAPI) → JSON API → Frontend
```

**(b) Batch data** (backtest / analysis results):
```
Python script → DataFrame → Parquet / CSV / JSON
  → Dashboard reads file directly (Streamlit) or via API
```

**(c) Static generation** (reports):
```
Python script → Jinja2 template → HTML file
  → Serve via any static hosting or open locally
```

### Step 4: Core Components

Design the dashboard layout based on use case:

**Bot monitoring:**
- Connection status (exchange API, WebSocket)
- Open positions with unrealized PnL
- Trade history (recent N trades)
- Daily / cumulative PnL chart
- Alert log
- Health endpoint: `GET /health → { status, uptime, exchange_connected, daily_pnl }`

**Backtest viewer:**
- Equity curve (cumulative return over time)
- Drawdown chart
- Trade distribution (win/loss, duration, size)
- Parameter sensitivity heatmap (if optimization was run)
- Summary statistics table (Sharpe, DD, win rate, PF)

**Portfolio / risk:**
- Asset allocation pie/treemap
- Sector exposure bar chart
- VaR / CVaR gauge
- Correlation heatmap
- Historical performance comparison

**Research / IR report:**
- Company overview card
- Financial metrics table (multi-period)
- Bull / bear case summary
- Peer comparison table
- Rendered from Markdown or structured data

### Step 5: Implementation

Implement using the selected stack. Apply these principles regardless of technology:

- **Separation**: Data fetching / processing and rendering are separate modules
- **Configuration**: Dashboard parameters (refresh interval, data path, symbols) via environment variables or config file — not hardcoded
- **Error handling**: Dashboard must not crash on missing data — show "no data" state gracefully
- **Responsive**: Layout should work on both desktop and mobile browsers

### Step 6: Codex Review (for complex dashboards)
```bash
codex -a on-request "Review this dashboard implementation:
{code}

Check:
1. Data/view separation (no business logic in templates)
2. Error handling (missing data, API failures, stale data)
3. Security (no secrets exposed in frontend, CORS configured correctly)
4. Performance (pagination for large datasets, lazy loading)"
```

### Step 7: Deployment

| Method | When to use |
|--------|------------|
| `uv run streamlit run app.py` | Local development, quick prototyping |
| `npm run build` → static hosting | Report viewers, no backend needed |
| Docker service in `docker-compose.yml` | Production bot monitoring |
| Cron + static HTML generation | Periodic reports, no running server |
| `uv run uvicorn app:app` | API-backed dashboards |
