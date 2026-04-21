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

## Testing Requirements

- **Testnet/sandbox mandatory**: All new bots must pass testnet before live
- **Dry-run mode**: Every bot must support `--dry-run` flag (log orders without executing)
- **Paper trading**: Simulate execution with real market data, fake orders
- **Integration tests**: Test with real exchange sandbox API
- **Stress tests**: Simulate rapid price changes, connection drops, partial fills
