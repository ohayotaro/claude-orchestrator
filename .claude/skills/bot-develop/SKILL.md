---
name: bot-develop
description: Develop API-based automated trading bots using ccxt, python-binance, and WebSocket. Covers architecture, order management, position tracking, and testnet verification.
agent: bot-engineer
context: fork
allowed-tools: "Bash(python *) Bash(uv *) Bash(pytest *) Bash(codex *) Read Write Edit Glob Grep"
---

# API Bot Development

Build automated trading bots that execute via exchange APIs.

## Workflow

### Step 1: Requirements
Ask the user:
1. Target exchange(s)
2. Market type (spot, futures/swap, margin)
3. Trading pair(s)
4. Strategy to implement (reference from `src/strategies/`)
5. Execution mode (REST polling, WebSocket event-driven, or hybrid)

### Step 2: Exchange API Specification Research (MANDATORY)

**No implementation may begin until the target exchange's API spec is documented.**

Research via Gemini CLI or official documentation:
- REST API: base URL, authentication (HMAC, API key header), order endpoints, position endpoints
- WebSocket API: connection URL, protocol (JSON-RPC, proprietary), subscription format, heartbeat
- Rate limits: requests per second/minute, weight system, order-specific limits
- Order types supported: market, limit, stop, trailing — and their parameters
- WebSocket message format: execution stream, order update stream, position stream
- Error codes: order rejection reasons, insufficient balance, rate limit exceeded
- Testnet/sandbox: availability, base URL, how to enable

Document in `src/data/api_specs/{exchange_name}.md`.

If using ccxt: verify that ccxt's implementation matches the exchange's current API version (ccxt may lag behind or have bugs for specific exchanges).

### Step 3: Architecture Design
Using the **bot-engineer** subagent, design based on researched API spec:
- Execution engine (ccxt async or direct exchange SDK — choose based on API spec findings)
- Order manager (state machine: create → submit → open → fill/cancel, matching exchange's actual order lifecycle)
- Position tracker (real-time PnL, unrealized/realized)
- WebSocket manager (price streams, order updates, reconnection — matching exchange's actual protocol)
- Risk controller (pre-trade checks, position limits)
- Configuration (environment variables, CLI args)

### Step 4: Implementation

**Assess scope**: Count the independent modules to implement from Step 3's architecture design.

| Modules to implement | Action |
|---------------------|--------|
| 1-2 modules | Implement directly in this skill |
| 3+ modules | **Transition to `/team-implement`** — assign each module to a specialist agent |

**If transitioning to `/team-implement`**, pass the architecture from Step 3 as input:
```
Module assignments:
- bot-engineer   → src/bot/executor.py (order execution, rate limiting)
- bot-engineer   → src/bot/websocket_manager.py (streams, reconnection)
- bot-engineer   → src/bot/position_tracker.py (PnL, reconciliation)
- quant-analyst  → src/bot/risk_controller.py (pre-trade checks, limits)
Interface contracts: {define function signatures between modules}
```

**If implementing directly** (1-2 modules), create in `src/bot/`:

**executor.py** — Order execution engine:
- Exchange connection management
- Order placement with retry logic
- Order status polling / WebSocket updates
- Rate limit handling

**position_tracker.py** — Position management:
- Real-time position state
- PnL calculation (unrealized + realized)
- Reconciliation with exchange state

**websocket_manager.py** — Stream management:
- Price feed subscription
- Order update stream
- Auto-reconnect with exponential backoff
- Message queue for processing

### Step 5: Implement Structured Logging
Implement the log events defined in `bot-development.md` "Structured Logging Contract":
- Lifecycle events: `bot_started`, `bot_stopped`, `bot_heartbeat` (every 60s)
- Order events: `order_created`, `order_submitted`, `order_filled`, `order_cancelled`, `order_rejected`
- Position events: `position_opened`, `position_closed`, `position_update` (every 30s while open)
- Safety events: `safety_triggered`, `reconnect`, `reconciliation`
- Performance snapshots: `perf_snapshot` (every 5 min)

All events output as JSONL to stdout + `logs/bot.jsonl`. This is the contract that enables `/bot-monitor`, `/incident-response`, and `/dashboard-develop` to consume bot state.

### Step 6: Implement Risk Controls
- Pre-trade balance check
- Position size limit enforcement
- Daily loss limit check
- Max concurrent orders check
- Spread/slippage guard

### Step 7: Implement Dry-Run Mode
- `--dry-run` flag: log orders without executing
- Paper trading: simulate fills with real market data
- Same code path as live — only the exchange client is mocked

### Step 8: Testnet Verification
1. Run on exchange testnet/sandbox
2. Place and cancel orders
3. Verify position tracking accuracy
4. Test reconnection (kill WebSocket, verify recovery)
5. Test emergency stop procedure

For full code quality review (async correctness, error handling, race conditions), run `/team-review`.
