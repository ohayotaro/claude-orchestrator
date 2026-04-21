---
name: dashboard-develop
description: Build real-time trading dashboards with FastAPI backend and Vite + Lightweight Charts frontend. Covers health endpoints, metrics API, and live chart display.
agent: infra-ops
allowed-tools: "Bash(python *) Bash(uv *) Bash(npm *) Bash(npx *) Read Write Edit Glob Grep"
---

# Trading Dashboard Development

Build real-time monitoring dashboards for trading bots.

## Workflow

### Step 1: Requirements
Ask the user:
1. Dashboard type (simple status page, full trading UI, admin panel)
2. Data sources (bot health API, trade logs, JSONL events)
3. Charts needed (candlestick, equity curve, PnL, positions)
4. Update frequency (real-time WebSocket, polling, static cron)
5. Deployment (local, static hosting, Docker)

### Step 2: Backend (FastAPI)
Design API endpoints:
```
GET /health   → Bot health status (200 OK / 503 unhealthy)
GET /metrics  → Trading metrics (PnL, trades, positions, uptime)
GET /status   → Combined health + metrics + signal state
GET /trades   → Recent trade history (paginated)
GET /chart    → OHLCV data for charting
```

Implementation:
- FastAPI with uvicorn
- CORS middleware for frontend access
- JSON response format
- Parse structlog JSONL files or query bot state DB

### Step 3: Frontend (Vite SPA)
Tech stack:
- **Vite** — Fast build tool and dev server
- **Lightweight Charts** (TradingView) — Interactive candlestick charts
- **Tailwind CSS** — Utility-first styling
- Vanilla JS or minimal framework

Key components:
- Real-time price chart with indicators
- PnL display (daily, cumulative)
- Position status panel
- Trade history table
- Connection status indicator
- Uptime display

### Step 4: Data Flow
```
Bot (structlog JSONL / SQLite)
  → FastAPI (parse/aggregate)
  → JSON API
  → Frontend (fetch + render)
  → Auto-refresh (60s interval or WebSocket)
```

### Step 5: Deployment
Options:
- **Local dev**: `uvicorn app:app --reload` + `npm run dev`
- **Static export**: `npm run build` → deploy dist/ to hosting
- **Docker**: Add dashboard service to docker-compose.yml
- **Cron + SCP**: Generate static data, push to remote server
