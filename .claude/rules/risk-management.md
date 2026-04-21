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
