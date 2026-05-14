---
name: bot-monitor
description: Set up monitoring, alerting, and dashboards for trading bots. Supports per-strategy, risk-group, and account-wide views. Covers structured logging, metrics, alert rules, and notification channels.
agent: infra-ops
context: fork
allowed-tools: "Bash(python *) Bash(docker *) Bash(uv *) Read Write Edit Glob Grep"
---

# Bot Monitoring Setup

Configure comprehensive monitoring for trading bots.

## Precondition: Invocation Modes

This skill operates in two modes. Determine the mode from the invocation arguments before proceeding.

- **Per-strategy mode**: invoked with `strategy_id`. Monitors one strategy's logs at `logs/strategies/{strategy_id}/bot.jsonl` (resolved via `log_path` in `config/registry.toml`) and produces a per-strategy dashboard.
- **Group mode**: invoked with `risk_group` (or no argument, defaulting to all groups). Reads `config/registry.toml` to discover the member strategies for the requested group(s), then aggregates across all members by reading `logs/strategies/*/bot.jsonl` for matched strategies.

In either mode, the skill MUST:
1. Read `config/registry.toml` to resolve strategy metadata (log paths, `risk_group`, `account_scope`, `state`, `enabled`).
2. Refuse to operate on a `strategy_id` not present in the registry (hint the user to run `/strategy-register`).
3. Include `strategy_id` in every metric query, alert event, and dashboard panel.

## Workflow

### Step 1: Requirements
Ask the user:
1. Invocation mode: per-strategy (`strategy_id`) or group (`risk_group` / all)
2. Notification channel (Slack, Discord, Telegram)
3. Monitoring depth (simple logging, full metrics stack)
4. Dashboard needs (none, simple HTML, Grafana)
5. Alert urgency levels needed

### Step 2: Structured Logging
Implement in `src/monitoring/`:
- JSON-formatted log output via structlog
- Standard fields: timestamp, level, `strategy_id`, symbol
- Every log event MUST include `strategy_id` (see `monitoring.md` "Per-Strategy Log Isolation")
- Trade event logging (orders, fills, positions, PnL) -- all filtered by `strategy_id`
- Performance logging (latency, API calls, errors) -- all tagged with `strategy_id`
- Log discovery: read `log_path` from `config/registry.toml` for each strategy. Do NOT hardcode `logs/bot.jsonl` or any single-bot path.

### Step 3: Metrics Collection
Define and instrument core metrics. Every metric MUST carry a `strategy_id` label.
- **Uptime**: bot running time per `strategy_id`, last restart reason
- **Trading**: orders/fills count, win rate (rolling), PnL -- per `strategy_id`
- **Execution**: API latency (p50, p95, p99), slippage -- per `strategy_id`
- **Connection**: WebSocket uptime, reconnect count -- per `strategy_id`
- **Errors**: API errors by type, rejected orders -- per `strategy_id`

In group mode, produce aggregate metrics alongside per-strategy breakdowns:
- Group-level net + gross exposure (sum across member strategies)
- Group-level daily PnL (sum of per-strategy PnL)
- Group-level open position count

### Step 4: Alert Rules
Configure alerts per `monitoring.md` thresholds. Every alert event MUST include `strategy_id`.
- Exchange disconnection (>30s warning, >120s critical)
- Daily loss limit (>3% warning, >5% critical)
- API error rate (>1% warning, >5% critical)
- Consecutive order rejections (3x warning)
- No heartbeat (>60s critical)

In group mode, additionally configure group-level alerts from `risk-management.md` "Cross-Strategy Risk Aggregation":
- Group daily loss soft cap (default 3%) -> WARNING
- Group daily loss hard cap (default 5%) -> CRITICAL
- Account margin breach (>95%) -> CRITICAL

### Step 5: Notification Setup
Configure webhook integration. The notification payload MUST surface `strategy_id`, `risk_group`, and severity at the top:
```python
# Alert message format
{
    "severity": "WARNING|CRITICAL",
    "strategy_id": "binance.swap.mean-revert.btcusdt.5m.v1",
    "risk_group": "crypto-main",
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

### Step 6: Dashboard
**Per-strategy dashboard** (always generated in per-strategy mode):
- Current positions, PnL, order history for one `strategy_id`
- Connection status, uptime for that strategy
- Tag the dashboard with `strategy_id`

**Group-level overview dashboard** (generated in group mode):
- One panel per member strategy showing key metrics (PnL, position count, uptime)
- Aggregate panels: group net exposure, group daily PnL, group drawdown vs. high-water mark
- Tag the dashboard with `risk_group`

For simple monitoring:
- HTML dashboard served by bot's health endpoint

For full monitoring:
- Prometheus metrics endpoint (`/metrics`) -- all metrics labeled with `strategy_id`
- Generate one Grafana dashboard per strategy AND a group-level overview dashboard
- Use `strategy_id` as the primary dashboard variable/tag
- Docker Compose service for Prometheus + Grafana

### Step 7: Log Rotation
Configure per-strategy log rotation (each strategy's `bot.jsonl` rotates independently):
- Docker: `json-file` driver, `max-size: 100m`, `max-file: 5`
- VPS: logrotate configuration per strategy log path
- Retention: 30 days compressed

Log aggregation reads from `logs/strategies/*/bot.jsonl` (glob across registered strategies). Do NOT read from a single `logs/bot.jsonl`.

## Multi-Strategy Notification Patterns

- **Per-strategy alerts** go to the notification channel configured in the strategy's per-strategy config (`config/strategies/{strategy_id}.toml`). If no per-strategy channel is configured, fall back to the project default channel.
- **Risk-group aggregate alerts** go to the risk-group channel defined in `config/risk_groups.toml`.
- **CRITICAL alerts always escalate** to all configured channels regardless of routing config. CRITICAL severity bypasses per-strategy and per-group routing to ensure visibility.
