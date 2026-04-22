---
name: incident-response
description: Handle trading bot incidents. Covers emergency stop, root cause analysis via Codex, recovery procedures, and postmortem documentation.
allowed-tools: "Bash(python *) Bash(docker *) Bash(codex *) Bash(git *) Read Write Edit Glob Grep"
---

# Incident Response

Handle trading bot failures and emergencies.

## Incident Classification

| Severity | Examples | Response Time |
|----------|----------|--------------|
| **P0 — Critical** | Uncontrolled losses, position stuck, account at risk | Immediate |
| **P1 — High** | Exchange disconnected >2min, orders rejected repeatedly | < 5 minutes |
| **P2 — Medium** | Elevated error rate, degraded performance | < 30 minutes |
| **P3 — Low** | Minor logging issues, non-critical warnings | Next session |

## Workflow

### Step 1: Immediate Triage
Determine severity and take immediate action:

**P0 — Critical:**
1. Emergency stop: close all positions, cancel pending orders
2. Stop bot: `docker compose down` or `systemctl stop bot`
3. Notify stakeholders immediately
4. Proceed to root cause analysis

**P1 — High:**
1. Pause new entries (keep existing positions)
2. Investigate connection / API status
3. If unresolved in 5 minutes → escalate to P0

**P2/P3:**
1. Log the issue
2. Continue monitoring
3. Fix in next maintenance window

### Step 2: Emergency Stop Procedure
```bash
# 1. Cancel all pending orders
python -c "from src.bot.executor import emergency_stop; emergency_stop()"

# 2. Close all positions (market orders)
python -c "from src.bot.executor import close_all_positions; close_all_positions()"

# 3. Stop the bot
docker compose down
# OR
systemctl stop trading-bot

# 4. Verify on exchange
# Manually check exchange UI for any remaining positions
```

### Step 3: Root Cause Analysis
Gather evidence and delegate to Codex:
1. Collect logs: `docker compose logs --tail 500 > incident.log`
2. Check exchange status page
3. Review recent code changes: `git log --oneline -10`

```bash
codex exec --full-auto "Analyze this trading bot incident:

Error logs:
{paste relevant logs}

Bot state at time of incident:
- Open positions: {list}
- Pending orders: {list}
- Exchange connection: {status}
- Last successful trade: {timestamp}

Determine:
1. Root cause
2. Impact assessment (positions affected, PnL impact)
3. Fix recommendation
4. Prevention measures"
```

### Step 4: Recovery
After root cause is identified and fixed:
1. Deploy fix to testnet first
2. Run verification tests
3. Staged restart (minimum size first)
4. Monitor closely for 1 hour
5. Gradually return to normal operation

### Step 5: Postmortem
Document in `.claude/docs/incidents/`:

```markdown
# Incident: {title}
Date: {date}
Severity: P{0-3}
Duration: {time to resolution}

## Summary
{1-2 sentences}

## Timeline
- HH:MM — First alert
- HH:MM — Action taken
- HH:MM — Root cause identified
- HH:MM — Fix deployed
- HH:MM — Normal operation resumed

## Root Cause
{description}

## Impact
- Positions affected: N
- PnL impact: $X
- Downtime: N minutes

## Resolution
{what was done}

## Prevention
{what changes to make so this doesn't happen again}
```

### Step 6: Prevention Actions
- Update bot code if bug was found
- Update alert thresholds if detection was slow
- Update monitoring if blind spot was found
- Update this incident response procedure if process failed
