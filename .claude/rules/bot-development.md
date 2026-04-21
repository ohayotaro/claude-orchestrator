# Bot Development Rules

## ccxt Standard Patterns

### Exchange Initialization
```python
import ccxt.async_support as ccxt

exchange = ccxt.binance({
    "apiKey": os.environ["BINANCE_API_KEY"],
    "secret": os.environ["BINANCE_SECRET_KEY"],
    "sandbox": True,  # Always start with sandbox/testnet
    "enableRateLimit": True,  # Mandatory
    "options": {"defaultType": "swap"},  # spot, swap, future
})
```

### Order Lifecycle
- Always use `create_order()` with explicit parameters (not shortcuts)
- Check order status after placement: `fetch_order(id, symbol)`
- Handle partial fills: track `filled` vs `amount`
- Implement timeout for pending orders (cancel after N seconds)
- Log every state transition: created → open → partial → filled/cancelled

## WebSocket Management

### Mandatory Patterns
- Auto-reconnect with exponential backoff (1s, 2s, 4s, 8s... max 60s)
- Heartbeat/ping-pong monitoring (detect stale connections)
- Separate streams for: price data, order updates, position changes
- Message queue for processing (prevent backpressure)
- Graceful shutdown: unsubscribe before disconnect

### Connection Health
```python
# Check connection health every 30 seconds
# If no message received in 60 seconds → reconnect
# If 3 consecutive reconnect failures → alert + pause trading
```

## asyncio Best Practices

- Use `asyncio.gather()` for concurrent API calls
- Never use `time.sleep()` — always `await asyncio.sleep()`
- Implement proper cancellation with `asyncio.shield()` for critical operations
- Use `asyncio.Queue` for producer-consumer patterns
- Handle `asyncio.CancelledError` for graceful shutdown

## Rate Limiting

- Always enable ccxt's built-in rate limiter (`enableRateLimit: True`)
- For burst operations, implement custom token bucket
- Log rate limit warnings (HTTP 429 responses)
- Different limits for: REST orders, REST queries, WebSocket subscriptions

## Order State Machine

```
CREATED → SUBMITTED → OPEN → PARTIALLY_FILLED → FILLED
                         │                         │
                         └→ CANCELLED              └→ CANCELLED (partial)
                         │
                         └→ REJECTED
                         │
                         └→ EXPIRED
```

- Track every transition with timestamp
- Store full order history in persistent storage
- Reconcile local state with exchange state periodically

## Exchange-Specific Adapters (Non-ccxt Exchanges)

For exchanges not fully supported by ccxt, build direct adapters:

### REST Client Pattern
```python
class ExchangeRestClient(Protocol):
    async def get_ticker(self, symbol: str) -> Ticker: ...
    async def get_positions(self) -> list[Position]: ...
    async def place_order(self, order: OrderRequest) -> OrderResult: ...
    async def cancel_order(self, order_id: str) -> None: ...
    async def get_balance(self) -> Balance: ...
```

- HMAC-SHA256 signature for private endpoints
- Per-endpoint rate limiting (internal RateLimiter class)
- Retry on 429/500/502/503 with exponential backoff

### WebSocket Client Pattern
- JSON-RPC 2.0 or exchange-specific protocol
- Channel subscription management
- Watchdog timer (restart on N seconds of silence)
- Auto-reconnect with exponential backoff (1s → 30s cap)

## State Persistence (Pluggable Backend)

### StateStore Protocol
```python
class StateStore(Protocol):
    async def save_position(self, position: Position) -> None: ...
    async def load_positions(self) -> list[Position]: ...
    async def save_trade(self, trade: Trade) -> None: ...
    async def load_trades(self, since: datetime) -> list[Trade]: ...
    async def save_checkpoint(self, state: dict) -> None: ...
    async def load_checkpoint(self) -> dict | None: ...
```

### Recommended Default (SQLite + WAL)

SQLite with WAL mode is the recommended default. PostgreSQL, Redis, or other backends can be used depending on project requirements.

```python
# aiosqlite with WAL for concurrent read/write safety
async with aiosqlite.connect("bot_state.db") as db:
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA synchronous=NORMAL")
    await db.execute("PRAGMA busy_timeout=5000")
```

### Required Tables
- **positions**: Current open positions (symbol, side, size, entry_price, timestamp)
- **trades**: Completed trade history (entry, exit, PnL, duration)
- **checkpoints**: Bot state snapshots for crash recovery

### Crash Recovery Protocol
1. On startup, query exchange for actual positions
2. Compare with stored state in SQLite
3. If mismatch: reconcile (exchange state = source of truth)
4. If 3+ consecutive mismatches: emergency shutdown + alert
5. Resume normal operation only after reconciliation

## Equity Market Execution Patterns

### Trading Hours Awareness
```python
from datetime import time
from zoneinfo import ZoneInfo

# Example: TSE trading hours
MARKET_HOURS = {
    "pre_open": (time(8, 0), time(9, 0)),    # Pre-open
    "morning": (time(9, 0), time(11, 30)),     # Morning session
    "lunch": (time(11, 30), time(12, 30)),     # Lunch break
    "afternoon": (time(12, 30), time(15, 0)),  # Afternoon session
}

# Must check: is_market_open() before placing orders
# Must handle: session boundaries, half-days, holidays
```

### Order Types for Equity
- **Market orders**: Use sparingly — slippage risk in thin stocks
- **Limit orders**: Preferred — specify price, respect tick size
- **MOO/MOC** (Market-on-Open/Close): For auction participation
- **Stop orders**: Not available on all exchanges — implement client-side if needed

### Broker API Patterns
Equity brokers use different protocols than crypto exchanges:
- **FIX protocol**: Institutional standard (Interactive Brokers, etc.)
- **REST/WebSocket**: Newer retail APIs
- **Proprietary**: Some brokers have unique SDKs
- **Key difference**: Order acknowledgment flow may include exchange-level confirmations

## Testing Requirements

- **Testnet/sandbox mandatory**: All new bots must pass testnet before live
- **Dry-run mode**: Every bot must support `--dry-run` flag (log orders without executing)
- **Paper trading**: Simulate execution with real market data, fake orders
- **Integration tests**: Test with real exchange sandbox API
- **Stress tests**: Simulate rapid price changes, connection drops, partial fills
- **Replay tests**: Bit-exact replay of historical tick data to verify signal parity
