---
name: notification-setup
description: Integrate notification channels (Discord, LINE, Telegram) for trading bot alerts. Fire-and-forget pattern with structured event messages.
agent: bot-engineer
allowed-tools: "Bash(python *) Bash(uv *) Read Write Edit Glob Grep"
---

# Notification System Setup

Configure alert channels for trading bot events.

## Workflow

### Step 1: Channel Selection
Ask the user which channels to configure:
1. **Discord** — Webhook URL (easiest setup)
2. **LINE Messaging API** — Channel access token + user ID
3. **Telegram Bot** — Bot token + chat ID
4. Multiple channels supported simultaneously

### Step 2: Event Definitions
Configure which events trigger notifications:

| Event | Severity | Example |
|-------|----------|---------|
| Trade entry/exit | INFO | "BUY {amount} {symbol} @ {price}" |
| Daily PnL summary | INFO | "Daily PnL: {amount} ({percent}%)" |
| Safety gate triggered | WARNING | "Safety gate activated: {gate_name} ({details})" |
| Connection lost | WARNING | "Exchange WebSocket disconnected" |
| Emergency stop | CRITICAL | "Daily loss limit reached ({amount})" |
| Bot start/stop | INFO | "Bot started: tick_rsi v2.1" |
| Position mismatch | CRITICAL | "Position reconciliation failed 3x" |

### Step 3: Implementation Pattern

**Fire-and-forget** — notification failures MUST NOT block trading:
```python
async def notify(message: str, severity: str = "INFO") -> None:
    try:
        async with asyncio.timeout(5):
            await _send_to_channels(message, severity)
    except Exception:
        logger.warning("notification_failed", message=message)
        # Never raise — trading continues regardless
```

### Step 4: Discord Webhook
```python
async def send_discord(webhook_url: str, message: str) -> None:
    # Validate URL prefix: https://discord.com/api/webhooks/
    async with httpx.AsyncClient() as client:
        await client.post(webhook_url, json={"content": message})
```

### Step 5: LINE Messaging API
```python
async def send_line(token: str, user_id: str, message: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    body = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://api.line.me/v2/bot/message/push",
            headers=headers, json=body
        )
```

### Step 6: Telegram Bot
```python
async def send_telegram(token: str, chat_id: str, message: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": chat_id, "text": message})
```

### Step 7: Configuration
Add to `.env`:
```bash
# Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx/yyy

# LINE
LINE_CHANNEL_TOKEN=xxx
LINE_USER_ID=Uxxx

# Telegram
TELEGRAM_BOT_TOKEN=xxx:yyy
TELEGRAM_CHAT_ID=123456
```

### Step 8: Testing
- Send test notification to each configured channel
- Verify fire-and-forget (simulate failure, confirm bot continues)
- Test rate limiting (don't spam channels during volatile markets)
