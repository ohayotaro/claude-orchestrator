---
name: bot-monitor
description: Set up monitoring, alerting, and dashboards for trading bots. Covers structured logging, metrics, alert rules, and notification channels.
agent: infra-ops
context: fork
allowed-tools: "Bash(python *) Bash(docker *) Bash(uv *) Read Write Edit Glob Grep"
---

# Bot Monitoring Setup

Configure comprehensive monitoring for trading bots.

## Workflow

### Step 1: Requirements
Ask the user:
1. Notification channel (Slack, Discord, Telegram)
2. Monitoring depth (simple logging, full metrics stack)
3. Dashboard needs (none, simple HTML, Grafana)
4. Alert urgency levels needed

### Step 2: Structured Logging
Implement in `src/monitoring/`:
- JSON-formatted log output via structlog
- Standard fields: timestamp, level, bot_name, strategy, symbol
- Trade event logging (orders, fills, positions, PnL)
- Performance logging (latency, API calls, errors)

### Step 3: Metrics Collection
Define and instrument core metrics:
- **Uptime**: bot running time, last restart reason
- **Trading**: orders/fills count, win rate (rolling), PnL
- **Execution**: API latency (p50, p95, p99), slippage
- **Connection**: WebSocket uptime, reconnect count
- **Errors**: API errors by type, rejected orders

### Step 4: Alert Rules
Configure alerts per monitoring.md thresholds:
- Exchange disconnection (>30s warning, >120s critical)
- Daily loss limit (>3% warning, >5% critical)
- API error rate (>1% warning, >5% critical)
- Consecutive order rejections (3x warning)
- No heartbeat (>60s critical)

### Step 5: Notification Setup
Configure webhook integration:
```python
# Alert message format
{
    "severity": "WARNING|CRITICAL",
    "bot": "bot_name",
    "event": "event_type",
    "message": "Human-readable description",
    "timestamp": "ISO8601",
    "action_taken": "What the bot did automatically"
}
```

Channels:
- Slack: Incoming Webhook URL
- Discord: Webhook URL
- Telegram: Bot token + chat ID

### Step 6: Dashboard (Optional)
For simple monitoring:
- HTML dashboard served by bot's health endpoint
- Current positions, PnL, order history
- Connection status, uptime

For full monitoring:
- Prometheus metrics endpoint (`/metrics`)
- Grafana dashboard with pre-built panels
- Docker Compose service for Prometheus + Grafana

### Step 7: Log Rotation
Configure:
- Docker: `json-file` driver, `max-size: 100m`, `max-file: 5`
- VPS: logrotate configuration
- Retention: 30 days compressed
