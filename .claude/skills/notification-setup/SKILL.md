---
name: notification-setup
description: Design the notification routing from bot log events to alert channels. Define which events trigger notifications, at what severity, in what format, and to which channel.
agent: bot-engineer
allowed-tools: "Bash(python *) Bash(uv *) Read Write Edit Glob Grep"
---

# Notification Routing Design

Design how bot log events (defined in `bot-development.md` Structured Logging Contract) are routed to notification channels.

**This skill does NOT implement channel-specific API clients.** It designs the routing rules that the notification module consumes.

## Workflow

### Step 1: Identify Available Log Events
Read the Structured Logging Contract from `bot-development.md`. The following event categories are available as notification sources:

| Category | Events | Default Frequency |
|----------|--------|-------------------|
| Lifecycle | `bot_started`, `bot_stopped`, `bot_heartbeat` | heartbeat: 60s |
| Orders | `order_created`, `order_submitted`, `order_filled`, `order_cancelled`, `order_rejected` | Per occurrence |
| Positions | `position_opened`, `position_closed`, `position_update` | update: 30s |
| Safety | `safety_triggered`, `reconnect`, `reconciliation` | Per occurrence |
| Performance | `perf_snapshot` | 5 min |

### Step 2: Design Notification Rules
Ask the user which events should trigger notifications, then define the routing table:

```yaml
# notification_rules.yaml
rules:
  # --- CRITICAL: Always notify immediately ---
  - event: bot_stopped
    condition: "reason != 'user'"       # Only unexpected stops
    severity: CRITICAL
    channels: [primary, backup]
    format: "[CRITICAL] Bot stopped unexpectedly: {reason} (uptime: {uptime_s}s)"

  - event: safety_triggered
    severity: CRITICAL
    channels: [primary, backup]
    format: "[CRITICAL] Safety gate: {gate} — {details}. Action: {action}"

  - event: reconciliation
    condition: "status == 'mismatch'"
    severity: CRITICAL
    channels: [primary]
    format: "[CRITICAL] Position mismatch: local={local_size} exchange={exchange_size}"

  - event: order_rejected
    severity: WARNING
    channels: [primary]
    format: "[WARNING] Order rejected: {order_id} — {reason}"

  # --- WARNING: Notify but not urgent ---
  - event: reconnect
    condition: "attempt >= 3"           # Only after repeated failures
    severity: WARNING
    channels: [primary]
    format: "[WARNING] Reconnection attempt #{attempt} for {target} (backoff: {backoff_s}s)"

  # --- INFO: Periodic summary, not per-event ---
  - event: position_closed
    severity: INFO
    channels: [primary]
    format: "Closed {side} {symbol}: PnL {pnl} ({pnl_pct}%) | held {holding_s}s"

  - event: bot_started
    severity: INFO
    channels: [primary]
    format: "Bot started: {strategy} v{version}"

  # --- SUMMARY: Aggregated, not real-time ---
  - event: perf_snapshot
    severity: SUMMARY
    channels: [primary]
    throttle: "1h"                      # Max 1 notification per hour
    format: "Hourly: PnL={daily_pnl} | Latency p99={api_latency_p99_ms}ms | Errors={api_errors_1h}"
```

### Step 3: Define Severity → Channel Mapping
Map severities to notification channels. Channels are configured in `.env` — this step only defines the routing logic, not the channel implementation.

```yaml
channels:
  primary:
    description: "Main alert channel (e.g., Discord, Slack, Telegram)"
    env_var: "NOTIFY_PRIMARY_URL"
    
  backup:
    description: "Backup channel for CRITICAL events (e.g., SMS, LINE, email)"
    env_var: "NOTIFY_BACKUP_URL"

severity_routing:
  CRITICAL: [primary, backup]    # Redundant delivery for critical events
  WARNING:  [primary]
  INFO:     [primary]
  SUMMARY:  [primary]
```

### Step 4: Define Throttling and Rate Limits
Prevent notification spam during volatile markets:

| Rule | Default | Rationale |
|------|---------|-----------|
| Max notifications per minute | 10 | Prevent spam during rapid order activity |
| CRITICAL events bypass throttle | yes | Safety events must always deliver |
| SUMMARY events max frequency | 1 per hour | Aggregate, don't stream |
| Duplicate suppression window | 60s | Same event+message within window → skip |
| Quiet hours (optional) | none | User-configurable; CRITICAL bypasses |

### Step 5: Define the Notification Interface
The notification module implements this interface. Channel-specific clients (Discord, Telegram, etc.) are pluggable backends.

```python
class NotificationRouter(Protocol):
    async def notify(self, event: dict) -> None:
        """Route a log event through the rules table.
        
        Args:
            event: A dict matching the Structured Logging Contract schema.
                   Must contain 'event' (str) and 'ts' (ISO8601) at minimum.
        
        Behavior:
            1. Match event['event'] against rules table
            2. Evaluate condition (if any)
            3. Check throttle/rate limits
            4. Format message using the rule's format template
            5. Send to mapped channels (fire-and-forget)
            6. Log delivery success/failure (never raise)
        """
        ...
```

### Step 6: Output
Save notification routing config to `src/monitoring/notification_rules.yaml` (or `.json`).

This file is consumed by the notification module at bot startup. Changes to routing rules do not require code changes — only config edits.

### Step 7: Validate
- [ ] Every CRITICAL log event has a routing rule
- [ ] CRITICAL rules route to both primary and backup channels
- [ ] Throttle rules prevent >10 notifications/minute (except CRITICAL)
- [ ] Format strings reference only fields that exist in the Structured Logging Contract
- [ ] fire-and-forget: notification failure does not block bot execution
