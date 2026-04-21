---
name: ml-pipeline
description: Build ML model training and evaluation pipelines for financial time series. Covers feature engineering, walk-forward validation with purge/embargo, hyperparameter tuning via Optuna, and overfitting detection.
agent: ml-engineer
allowed-tools: "Bash(python *) Bash(uv *) Bash(pytest *) Bash(codex *) Read Write Edit Glob Grep"
---

# ML Pipeline Builder

Develop, train, and validate ML models for financial applications.

## Workflow

### Step 1: Problem Definition
Ask the user:
1. Task type (classification: regime/action labels, regression: return prediction)
2. Target variable (regime labels, LONG/SHORT/FLAT actions, price direction)
3. Prediction horizon (1-bar, N-bar, variable)
4. Available data (OHLCV, tick data, order book)
5. Ground truth method if supervised (oracle labels, triple barrier, etc.)

### Step 2: Feature Engineering
Using the **ml-engineer** subagent:
- Design feature set from available data:
  - **Return-based**: log_return, abs_return, cumulative_return(N)
  - **Volatility**: realized_vol(N), Parkinson, Garman-Klass, ATR
  - **Technical**: SMA, EMA, RSI, MACD, ADX, Bollinger, via pandas-ta
  - **Price profiles**: OHLC/volume quantiles, price relative to range
  - **Lag features**: t-1, t-2, t-3 for supervised models
- Implement as immutable FeatureSet (df, feature_names)
- Validate feature computation is causal (no future data)

### Step 3: Data Splitting (Walk-Forward)
Design walk-forward protocol:
- **Expanding window** or **rolling window** (choose based on data stationarity)
- **Purge gap**: >= prediction horizon (prevent label leakage)
- **Embargo period**: additional buffer after purge (supervised models)
- **IS/OOS ratio**: minimum 70:30
- Validate that train/test boundaries are clean

### Step 4: Model Selection and Training
Choose and train model(s):
- **Unsupervised** (regime detection): HMM, GMM, K-Means, HDBSCAN, SOM
- **Supervised** (action/direction): LightGBM, CNN1D, MiniRocket
- **Hybrid**: Ensemble (voting, weighted), meta-learner

For each model:
1. Train on IS data only
2. Build label mapping on IS data (prevents label switching)
3. Apply to OOS data
4. Position shift(1) if generating trading signals (prevent 1-bar look-ahead)

### Step 5: Hyperparameter Optimization
Using Optuna (via Codex for complex search spaces):
```python
import optuna

def objective(trial):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 50, 500),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("lr", 0.01, 0.3, log=True),
    }
    # Walk-forward evaluation with purge/embargo
    return walk_forward_sharpe(model_class, params, data)

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=200)
```

### Step 6: Evaluation
Calculate and report:
- **Classification**: weighted F1, accuracy, confusion matrix per class
- **Trading**: Sharpe, return, max drawdown, win rate, PF
- **Temporal stability**: Prediction autocorrelation (key: r > 0.7 needed)
- **IS vs OOS gap**: Flag if > 30% degradation
- **Per-regime metrics**: Performance breakdown by market condition

### Step 7: Overfitting Detection
Delegate to Codex for rigorous assessment:
```bash
codex --approval-mode suggest "Assess overfitting risk:
- IS Sharpe: {is}, OOS Sharpe: {oos}
- Parameter count: {n_params}, Data points: {n_data}
- Feature count: {n_features}
Perform: Deflated Sharpe, CSCV, permutation test (H0: no skill)"
```

### Step 8: Ablation Analysis
- Remove each feature group → measure impact
- Remove each model component → measure impact
- Document which components are load-bearing vs noise

### Step 9: Integration
- Export trained model for inference
- Build inference pipeline (feature computation → predict → signal)
- Ensure inference uses only causal data (no future leakage)
- Add to strategy module in `src/strategies/`
