# Language Conventions

## No Emojis (Project-Wide)

Do not use emojis anywhere in this project — file contents (Markdown, code, comments), commit messages, log output, or chat replies. Use plain ASCII markers instead:

| Instead of | Use |
|---|---|
| `[x]` / `[ ]` checkboxes | (keep — these are ASCII) |
| `(ok)` / `(fail)` / `(warn)` | (preferred status markers) |
| `->` | (arrow — not the Unicode arrow) |
| `OK` / `NG` / `TODO` | (status / priority words) |
| plain bullet (`-`) | (no leading status emoji) |

When editing existing files, opportunistically strip any emojis encountered.

## Base Rules

| Target | Language | Notes |
|--------|----------|-------|
| User interaction | Japanese | Technical terms in English OK |
| Code | English | Including comments |
| Commit messages | English | Conventional Commits format |
| Documentation (user-facing) | Japanese | Code examples in English |
| Variable/function names | English | snake_case |
| Class names | English | PascalCase |
| File names | English | kebab-case or snake_case |
| Error/log messages | English | For log output |
| Agent instructions (.md) | English | Machine-consumed files |

## Conventional Commits

```
feat: add moving average crossover strategy
fix: correct Sharpe ratio calculation for negative returns
refactor: extract position sizing logic to separate module
test: add backtest validation for RSI strategy
docs: update data pipeline documentation
perf: optimize vectorbt backtest execution
chore: update dependencies in pyproject.toml
```

## Financial Term Mapping (Japanese → Code)

| Japanese | English (in code) |
|----------|-------------------|
| 移動平均 | moving_average |
| 損切り | stop_loss |
| 利確 | take_profit |
| ドローダウン | drawdown |
| 勝率 | win_rate |
| 損益比 | risk_reward_ratio |
| ポジションサイズ | position_size |
| 約定 | execution / fill |
| スリッページ | slippage |
| スプレッド | spread |
