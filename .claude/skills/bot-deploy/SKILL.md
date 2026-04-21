---
name: bot-deploy
description: Deploy trading bots with Docker, systemd, and environment management. Includes health checks, logging, and Codex deployment review.
agent: infra-ops
allowed-tools: "Bash(python *) Bash(docker *) Bash(uv *) Bash(codex *) Read Write Edit Glob Grep"
---

# Bot Deployment

Containerize and deploy trading bots to production.

## Workflow

### Step 1: Environment Assessment
Ask the user:
1. Deployment target (local Docker, VPS, cloud)
2. Number of bots to deploy
3. Uptime requirements (24/7, market hours only)
4. Monitoring preference (simple logging, Prometheus+Grafana)

### Step 2: Dockerfile Generation
Using the **infra-ops** subagent, create:
- Multi-stage Dockerfile (builder + runtime)
- `.dockerignore` file
- Non-root user configuration
- Health check endpoint

### Step 3: Docker Compose Configuration
Generate `docker-compose.yml`:
- Bot service(s) with restart policy
- Environment variable management
- Volume mounts for data persistence
- Network configuration
- Health check configuration
- Log driver configuration (JSON, max-size)

### Step 4: Environment Setup
- Generate `.env.production` template
- Configure secrets (API keys, webhook URLs)
- Set bot parameters (symbol, strategy, risk limits)
- Configure log level and output

### Step 5: Health Check Implementation
Add to bot:
```python
# GET /health → 200 OK
{
    "status": "healthy|degraded|unhealthy",
    "uptime_seconds": N,
    "exchange_connected": true|false,
    "last_heartbeat": "ISO8601",
    "open_positions": N,
    "daily_pnl": X.XX
}
```

### Step 6: systemd Service (VPS)
Generate systemd unit file for:
- Auto-start on boot
- Restart on failure (with backoff)
- Log to journald
- Environment file integration

### Step 7: Codex Deployment Review
```bash
codex -a on-request "Review this deployment configuration:
{Dockerfile + docker-compose.yml + systemd unit}

Check:
1. Security (non-root, no secrets in image, proper permissions)
2. Reliability (restart policy, health checks, graceful shutdown)
3. Logging (structured output, rotation, retention)
4. Resource limits (memory, CPU constraints)
5. Network security (exposed ports, firewall rules)"
```

### Step 8: Deploy
1. Build image: `docker compose build`
2. Start in detached mode: `docker compose up -d`
3. Verify health: `curl localhost:8080/health`
4. Check logs: `docker compose logs -f`
5. Run deployment checklist

### Step 9: Post-Deploy Verification
- Health check passing
- Exchange connected
- Orders executing (testnet first)
- Logs flowing correctly
- Alerts configured and tested
