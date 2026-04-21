# Risk Management Rules

## Mandatory Requirements for Automated Trading Systems

All EAs and Bots MUST implement the following risk controls:

### Position Management
- **Max position size**: Must not exceed N% of account balance (default: 2%)
- **Max concurrent positions**: Must not exceed defined limit
- **Cross-pair correlation**: Limit same-direction positions on highly correlated pairs

### Loss Limits
- **Per-trade max loss**: 1-2% of account balance
- **Daily max loss**: 5% of account balance
- **Weekly max loss**: 10% of account balance
- **Monthly max loss**: 20% of account balance

### Emergency Stop Mechanism (Mandatory Implementation)
```
1. Daily loss limit reached    → Stop new positions for the day
2. Max drawdown reached        → Close all positions + stop EA
3. Abnormal spread detected    → Pause new entries
4. Consecutive API errors      → Alert + stop trading
5. Sudden account balance drop → Full stop + notification
```

### Stop Loss
- **Mandatory**: Every position MUST have a stop loss
- Strategies without stop loss are NOT permitted
- Trailing stops recommended

## Backtest Risk Evaluation

### Mandatory Report Items
- Max drawdown (amount, ratio, duration)
- Sharpe Ratio / Sortino Ratio / Calmar Ratio
- Win rate / Profit Factor / Average risk-reward ratio
- Max consecutive losses
- Recovery Factor

### Warning Thresholds
| Metric | Warning | Danger |
|--------|---------|--------|
| Max Drawdown | > 20% | > 30% |
| Sharpe Ratio | < 1.0 | < 0.5 |
| Win Rate | < 40% | < 30% |
| Profit Factor | < 1.5 | < 1.2 |
| Recovery Factor | < 2.0 | < 1.0 |

## Multi-Layer Safety Gates (Production Bots)

Beyond basic risk limits, production bots MUST implement exchange-specific safety gates:

### Gate System
| Gate | Trigger | Action |
|------|---------|--------|
| **KillSwitch** | File-based (`data/KILL`) or signal | Immediate full stop, close all positions |
| **SFD Gate** | FX-Spot deviation approaches penalty threshold (e.g., >5% on bitFlyer) | Block new entries |
| **Funding Gate** | Approaching funding checkpoint time | Close positions before checkpoint |
| **Maintenance Gate** | Approaching exchange maintenance window | Close positions, pause bot |
| **Margin Monitor** | Margin ratio exceeds alert threshold (e.g., >80%) | Block entries; >95% → emergency close |
| **Daily Loss Limit** | Cumulative daily PnL exceeds threshold | Stop new entries for the day |

### Position Reconciliation
- Compare local position state with exchange state **every 30 seconds**
- Exchange state is always the source of truth
- If mismatch detected 3 consecutive times → emergency shutdown + alert
- On startup: always query exchange before resuming

### Safety Check Ordering
```
Pre-trade check sequence:
1. KillSwitch active?         → BLOCK (exit code 0, no restart)
2. Maintenance window?        → BLOCK (close positions)
3. Funding checkpoint near?   → BLOCK (close positions)
4. SFD gate triggered?        → BLOCK new entries
5. Margin ratio > threshold?  → BLOCK new entries
6. Daily loss limit hit?      → BLOCK new entries
7. Position size limit?       → BLOCK if exceeded
8. All clear                  → ALLOW trade
```
