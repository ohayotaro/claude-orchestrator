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

### Step 0: Validate Strategy is Registered

**Required argument**: `strategy_id` (first positional argument, e.g., `/bot-develop binance.swap.mean-revert.btcusdt.5m.v1`).

If `strategy_id` is not provided, refuse with:
```
Error: strategy_id is required.
Usage: /bot-develop {strategy_id}

Register a strategy first: /strategy-register register
```

Validation steps:
1. Call `/strategy-register show {strategy_id}` to confirm the entry exists.
2. Verify `runtime == "python"`. If `runtime == "mql5"`, refuse with: "This strategy uses MQL5 runtime. Use `/ea-generate {strategy_id}` instead."
3. If the entry does not exist, refuse with: "Strategy `{strategy_id}` not found in registry. Run `/strategy-register register` first."
4. Extract `config_path`, `state_path`, `log_path`, and `db_path` from the registry entry for use in all subsequent steps.

### Step 1: Requirements
Ask the user:
1. Target exchange(s)
2. Market type (spot, futures/swap, margin)
3. Trading pair(s)
4. Strategy to implement (reference from `src/strategies/`)
5. Execution mode (REST polling, WebSocket event-driven, or hybrid)

Note: the symbol, venue, and market are already recorded in the registry entry from Step 0. Use the registry values as defaults and confirm with the user if they differ.

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
- Configuration: `--strategy-id` is the required CLI arg. Config is loaded from the registry-resolved `config_path`. No other config file path may be accepted.
- State store: `StateStore` opens at the registry-resolved `db_path` (default: `state/strategies/{strategy_id}/state.db`).
- Logging: structured JSONL to `{log_path}/bot.jsonl` where `log_path` comes from the registry. Every log event includes `strategy_id`.

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

All generated code MUST follow the multi-strategy bot pattern from `bot-development.md`:
- Accept `--strategy-id` as a required CLI argument (no default).
- Resolve config from registry: `config/strategies/{strategy_id}.toml` (via registry lookup, never hardcoded).
- Open `StateStore` at registry-resolved `db_path` (`state/strategies/{strategy_id}/state.db`).
- Write logs to `{log_path}/bot.jsonl` (registry-resolved). Include `strategy_id` in every structured log event.
- On startup, validate registry entry: `enabled == true` and `state` permits the requested mode.
- Read `STRATEGY_ID` env var as a fallback when `--strategy-id` is not provided on CLI.

Do NOT generate code that hardcodes paths like `config.toml`, `bot_state.db`, or `logs/bot.jsonl`. All paths are derived from the registry entry.

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

All events output as JSONL to stdout + `{log_path}/bot.jsonl` (where `log_path` is resolved from the registry entry for this `strategy_id`). Every event MUST include `strategy_id` as a top-level field. This is the contract that enables `/bot-monitor`, `/incident-response`, and `/dashboard-develop` to consume bot state.

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
- Dry-run still requires `--strategy-id` and resolves all paths from the registry

### Step 8: Update Registry

After generating bot code, update the registry entry with runtime-specific fields that are now known:
- Call `/strategy-register` to fill in `db_path` if it was not populated at registration time.
- Do NOT edit `config/registry.toml` directly from this skill. All writes go through `/strategy-register`.

### Step 9: Testnet Verification
1. Run on exchange testnet/sandbox: `uv run python -m src.bot.main --strategy-id {strategy_id}`
2. Place and cancel orders
3. Verify position tracking accuracy
4. Test reconnection (kill WebSocket, verify recovery)
5. Test emergency stop procedure
6. Verify logs appear at `{log_path}/bot.jsonl` with `strategy_id` in every event
7. Verify state DB created at `{db_path}`

For full code quality review (async correctness, error handling, race conditions), run `/team-review`.
