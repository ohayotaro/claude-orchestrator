# Deployment Rules

## Docker Best Practices

### Dockerfile Standards
- Multi-stage builds (builder + runtime)
- Run as non-root user (`USER appuser`)
- Pin base image versions (e.g., `python:3.11-slim-bookworm`, never `:latest`)
- Copy only necessary files (use `.dockerignore`)
- Install dependencies before copying source (layer caching)
- Set `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1`

### Docker Compose
- Use named volumes for persistent data
- Set `restart: unless-stopped` for bot services
- Define health checks in compose file
- Use `.env` file for environment variables (never hardcode)
- Separate services: bot, monitoring, logging

## Environment Variables

### Mandatory
```bash
# Exchange credentials
EXCHANGE_API_KEY=
EXCHANGE_SECRET_KEY=

# Bot configuration
BOT_MODE=live|testnet|dry-run
BOT_SYMBOL=BTC/USDT
BOT_STRATEGY=

# Risk limits
MAX_POSITION_SIZE=
MAX_DAILY_LOSS=

# Monitoring
ALERT_WEBHOOK_URL=
LOG_LEVEL=INFO
```

### Rules
- All secrets via environment variables (never in code or Docker image)
- Use `.env` for local development, Docker secrets for production
- Different `.env` files per environment (`.env.testnet`, `.env.production`)
- Rotate API keys periodically

## Health Checks

### Mandatory for Every Bot
```python
# HTTP endpoint: GET /health → 200 OK
{
    "status": "healthy",
    "uptime_seconds": 3600,
    "exchange_connected": true,
    "last_heartbeat": "2026-04-21T12:00:00Z",
    "open_positions": 2,
    "daily_pnl": -0.5
}
```

- Health check interval: 30 seconds
- Unhealthy after 3 consecutive failures
- Auto-restart on unhealthy (Docker/systemd)

## systemd Service (VPS)

```ini
[Unit]
Description=Trading Bot - {strategy_name}
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=botuser
EnvironmentFile=/etc/bot/.env
ExecStart=/usr/bin/docker compose -f /opt/bot/docker-compose.yml up
ExecStop=/usr/bin/docker compose -f /opt/bot/docker-compose.yml down
Restart=on-failure
RestartSec=30
StartLimitInterval=300
StartLimitBurst=5

[Install]
WantedBy=multi-user.target
```

## CI/CD Pipeline

- Lint + type check on every push
- Run tests (unit + testnet integration) on PR
- Build Docker image on merge to main
- Deploy to staging first, then production (manual approval)
- Keep last 3 Docker image versions for rollback

## Rollback Procedure

1. Stop current bot: `docker compose down`
2. Verify all positions are closed or transferred
3. Switch to previous image version
4. Start: `docker compose up -d`
5. Verify health check passes
6. Monitor for 15 minutes before confirming

## macOS launchd Deployment

For local/dev deployment on macOS (alternative to Docker):

### plist Template
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "...">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.trading.{bot_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/.venv/bin/python</string>
        <string>-m</string>
        <string>src.bot.main</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/project</string>
    <key>KeepAlive</key>
    <true/>
    <key>ThrottleInterval</key>
    <integer>30</integer>
    <key>StandardOutPath</key>
    <string>/path/to/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/logs/stderr.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>DOTENV_PATH</key>
        <string>/path/to/.env</string>
    </dict>
</dict>
</plist>
```

### Service Management
```bash
# Load and start
launchctl load ~/Library/LaunchAgents/com.trading.{bot_name}.plist

# Stop and unload
launchctl unload ~/Library/LaunchAgents/com.trading.{bot_name}.plist

# Check status
launchctl list | grep trading

# View logs
tail -f /path/to/logs/stdout.log
```

### Notes
- KeepAlive: auto-restart on crash (respects ThrottleInterval)
- KillSwitch (exit code 0): does NOT trigger restart (clean exit)
- Use for development/single-machine setups; prefer Docker for production
