---
name: live-trading
description: Manage live trading execution. Covers testnet verification, production rollout, position monitoring, and performance comparison with backtest results.
agent: bot-engineer
allowed-tools: "Bash(python *) Bash(docker *) Read Write Edit Glob Grep"
---

# Live Trading Management

Safely transition from backtest to live trading.

## Workflow

### Step 1: Pre-Flight Checklist
Verify ALL items before going live:
- [ ] Strategy backtested with positive OOS results
- [ ] Bot passed testnet verification (all order types work)
- [ ] Dry-run mode tested with real market data
- [ ] Risk limits configured (max position, daily loss, stop loss)
- [ ] Emergency stop procedure documented and tested
- [ ] API keys have correct permissions (NO withdrawal)
- [ ] IP whitelist configured on exchange
- [ ] Monitoring and alerts configured
- [ ] Deployment environment ready (Docker/VPS)

### Step 2: Staged Rollout
1. **Phase A — Minimum size**: Run with smallest possible position size
   - Duration: 24-48 hours minimum
   - Verify: orders execute, positions track correctly, PnL matches expectations
2. **Phase B — Small size**: Increase to 25% of target position size
   - Duration: 1 week
   - Verify: performance consistent, no unexpected behavior
3. **Phase C — Target size**: Scale to full target position size
   - Monitor closely for first 48 hours

### Step 3: Live Monitoring
Track in real-time:
- Open positions and unrealized PnL
- Filled orders and execution quality (slippage)
- Connection status (exchange API, WebSocket)
- Account balance and margin usage
- Daily/weekly PnL

### Step 4: Performance Comparison
Compare live results to backtest:
| Metric | Backtest | Live | Acceptable Gap |
|--------|----------|------|----------------|
| Win Rate | X% | Y% | < 10% difference |
| Avg Slippage | 0 | Z bps | < 5 bps |
| Sharpe Ratio | X | Y | < 30% degradation |
| Max Drawdown | X% | Y% | Must not exceed 1.5x backtest |

If live performance significantly underperforms backtest → investigate or stop.

### Step 5: Emergency Procedures
If any trigger condition is met:
1. **Immediate**: Close all positions via emergency stop
2. **Investigate**: Use `/incident-response` skill
3. **Decide**: Fix and re-deploy, or halt strategy

### Step 6: Ongoing Operations
- Daily PnL review
- Weekly performance report vs backtest
- Monthly strategy review (edge still valid?)
- Quarterly parameter re-optimization
