---
name: init-finance
description: Initialize a financial trading project. Scaffold directories, dependencies, config files, and populate CLAUDE.md Zone B.
allowed-tools: "Bash(uv *) Bash(git *) Bash(mkdir *) Bash(ls *) Read Write Edit Glob"
---

# Initialize Financial Trading Project

Scaffold a complete financial trading project structure.

## Workflow

### Step 1: Gather Project Info
Ask the user:
1. Project name
2. Target markets (crypto, forex, futures — select all that apply)
3. Primary data sources (Binance, bybit, MT5, yfinance)
4. Backtest framework preference (backtrader, vectorbt, or both)

### Step 2: Create pyproject.toml
Generate `pyproject.toml` with:
- Project metadata
- Python >=3.11
- Core dependencies: pandas, numpy, backtrader/vectorbt, ccxt, yfinance, MetaTrader5
- Dev dependencies: pytest, ruff, mypy, pytest-cov

### Step 3: Scaffold Directories
```
src/data/          → __init__.py, fetcher.py, cleaner.py
src/strategies/    → __init__.py, base.py
src/backtesting/   → __init__.py, runner.py
src/optimization/  → __init__.py
src/risk/          → __init__.py, var.py, position_sizing.py
src/utils/         → __init__.py
mql5/experts/      → (empty, ready for EA files)
mql5/include/      → (empty, ready for shared libraries)
mql5/indicators/   → (empty, ready for custom indicators)
tests/             → conftest.py
data/              → .gitkeep
reports/           → .gitkeep
```

### Step 4: Generate .gitignore
Include: `data/`, `.env`, `*.pyc`, `__pycache__/`, `.claude/logs/`, `reports/*.html`, `uv.lock`

### Step 5: Generate .env.example
Template with all required API key placeholders.

### Step 6: Populate CLAUDE.md Zone B
Update the section between `@orchestra:template-boundary` and `@orchestra:repo-boundary` with project-specific info.

### Step 7: Install Dependencies
Run `uv sync` to install all dependencies.

### Step 8: Initialize Git
Run `git init` and create initial commit.
