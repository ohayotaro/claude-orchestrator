# Financial Domain Rules

## Numerical Precision

| Target | Precision | Example |
|--------|-----------|---------|
| Crypto prices | 8 decimal places | 0.00012345 BTC |
| FX prices | 5 decimals (JPY: 3) | 1.12345, 150.123 |
| Stock prices | 2 decimal places | 150.25 |
| Performance metrics | 4 decimal places | Sharpe: 1.5432 |
| Risk metrics | 2 decimals (%) | VaR: -2.35% |
| Lot size | 2 decimal places | 0.01 lot |

## Backtesting Principles

### Mandatory Rules
1. **No look-ahead bias**: Never use future data for signal generation
2. **Survivorship bias awareness**: Do not exclude delisted instruments
3. **Transaction costs**: Always include spread, commission, slippage
4. **Out-of-Sample testing mandatory**: IS/OOS ratio at minimum 70:30

### Recommended Practices
- Perform walk-forward analysis
- Run Monte Carlo simulation for robustness
- Test across multiple periods and markets
- Analyze drawdown periods in detail

## Risk Management

### Mandatory Definitions
- Max drawdown threshold (per strategy)
- Position sizing rules (fixed fraction, Kelly criterion, etc.)
- Stop loss (mandatory — no strategy without SL)
- Max concurrent positions
- Max risk per trade (N% of account)

### Emergency Stop Conditions
- Daily max loss reached → stop new positions for the day
- Consecutive loss count → halt trading
- Abnormal spread detected → pause entries
- API connection errors → alert + stop

## Data Quality

### Timezone
- **Standard**: UTC (Coordinated Universal Time)
- All timestamps unified to UTC
- Local time conversion only at display layer

### Missing Values
- Processing method must be explicitly stated (forward fill, interpolation, deletion, etc.)
- Warn when missing rate exceeds 5%
- Market holidays are exclusions, not missing data

### Data Source Reliability
- Document update frequency and latency for each source
- Note discrepancies between multiple sources
- Verify historical data adjustments (splits, dividends)
