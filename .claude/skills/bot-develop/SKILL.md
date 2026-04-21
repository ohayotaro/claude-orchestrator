---
name: bot-develop
description: Develop API-based automated trading bots using ccxt, python-binance, and WebSocket. Covers architecture, order management, position tracking, and testnet verification.
agent: bot-engineer
allowed-tools: "Bash(python *) Bash(uv *) Bash(pytest *) Bash(codex *) Read Write Edit Glob Grep"
---

# API Bot Development

Build automated trading bots that execute via exchange APIs.

## Workflow

### Step 1: Requirements
Ask the user:
1. Target exchange (Binance, bybit, etc.)
2. Market type (spot, futures/swap, margin)
3. Trading pair(s)
4. Strategy to implement (reference from `src/strategies/`)
5. Execution mode (REST polling, WebSocket event-driven, or hybrid)

### Step 2: Architecture Design
Using the **bot-engineer** subagent, design:
- Execution engine (ccxt async or exchange SDK)
- Order manager (state machine: create → submit → open → fill/cancel)
- Position tracker (real-time PnL, unrealized/realized)
- WebSocket manager (price streams, order updates, reconnection)
- Risk controller (pre-trade checks, position limits)
- Configuration (environment variables, CLI args)

### Step 3: Implement Core Components
Create modules in `src/bot/`:

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

### Step 4: Implement Risk Controls
- Pre-trade balance check
- Position size limit enforcement
- Daily loss limit check
- Max concurrent orders check
- Spread/slippage guard

### Step 5: Implement Dry-Run Mode
- `--dry-run` flag: log orders without executing
- Paper trading: simulate fills with real market data
- Same code path as live — only the exchange client is mocked

### Step 6: Codex Review
Delegate to Codex for async pattern and error handling review:
```bash
codex --approval-mode suggest "Review this trading bot for:
1. asyncio correctness (no blocking calls, proper cancellation)
2. Error handling (API errors, network failures, partial fills)
3. State consistency (position tracking accuracy)
4. Race conditions (concurrent order/fill events)
5. Graceful shutdown (pending orders, open positions)"
```

### Step 7: Testnet Verification
1. Run on exchange testnet/sandbox
2. Place and cancel orders
3. Verify position tracking accuracy
4. Test reconnection (kill WebSocket, verify recovery)
5. Test emergency stop procedure
