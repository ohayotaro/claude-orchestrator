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
src/risk/          → __init__.py, var.py, position_sizing.py, aggregator.py (stub for cross-strategy risk aggregation)
src/orchestrator/  → __init__.py, registry.py (stub for strategy registry interface)
src/utils/         → __init__.py
mql5/experts/      → (empty, ready for EA files)
mql5/include/      → (empty, ready for shared libraries)
mql5/indicators/   → (empty, ready for custom indicators)
tests/             → conftest.py
config/strategies/ → .gitkeep (per-strategy config files)
state/strategies/  → .gitkeep (per-strategy runtime state, gitignored)
logs/strategies/   → .gitkeep (per-strategy logs, gitignored)
reports/strategies/→ .gitkeep (per-strategy reports)
data/              → .gitkeep
reports/           → .gitkeep
```

### Step 3.5: Initialize Strategy Registry
Create multi-strategy infrastructure so the project supports running many strategies in parallel from day one. Reference: `.claude/rules/multi-strategy.md`.

1. Create `config/registry.toml` with the header schema (no strategy entries yet):
   ```toml
   schema_version = 1

   [defaults]
   state_dir = "state/strategies"
   log_dir = "logs/strategies"
   config_dir = "config/strategies"
   magic_range_start = 20_000_000
   magic_range_end = 89_999_999
   ```

2. Create `config/risk_groups.toml` skeleton:
   ```toml
   # Risk group definitions for cross-strategy risk aggregation.
   # Schema: one [[groups]] block per risk group.
   #
   # [[groups]]
   # name = "crypto-main"
   # soft_cap_daily_loss_pct = 3.0
   # hard_cap_daily_loss_pct = 5.0
   # margin_emergency_pct = 95.0
   # strategies = []  # populated automatically from registry.toml risk_group field
   #
   # Populate this file when the first strategies are registered.
   # See .claude/rules/multi-strategy.md section 6 for aggregation rules.
   ```

3. Verify `src/orchestrator/registry.py` stub exists (created in Step 3). The stub should contain a module docstring pointing to `.claude/skills/strategy-register/SKILL.md` for the full implementation and a placeholder `Registry` class.

4. Inform the user: to add a strategy, run `/strategy-register register`. Do not edit `config/registry.toml` by hand.

### Step 4: Generate .gitignore
Include: `data/`, `.env`, `*.pyc`, `__pycache__/`, `.claude/logs/`, `reports/*.html`, `state/strategies/*/`, `logs/strategies/*/`. Do NOT ignore `uv.lock` — it must be committed for reproducible builds (see `coding-principles.md`). Ensure `config/registry.toml` IS tracked (not gitignored).

### Step 5: Generate .env.example
Template with all required API key placeholders.

### Step 6: Populate CLAUDE.md Zone B
Update the section between `@orchestra:template-boundary` and `@orchestra:repo-boundary` with project-specific info.

Include a "Strategy Registry" note in Zone B:
```
### Strategy Registry
- Registry: `config/registry.toml` (source of truth for all strategy identities)
- Add strategies: `/strategy-register register`
- List strategies: `/strategy-register list`
- Contract: `.claude/rules/multi-strategy.md`
```

### Step 7: Install Dependencies
Run `uv sync` to install all dependencies.

### Step 8: Initialize Git
Run `git init` and create initial commit.

## Multi-Strategy Awareness

This scaffolded project supports running many strategies in parallel. Each strategy is addressed by a stable `strategy_id` and managed through `config/registry.toml`.

Key design decisions:
- **Identity**: every strategy has a unique `strategy_id` minted by `/strategy-register register`.
- **Isolation**: per-strategy config (`config/strategies/`), state (`state/strategies/`), logs (`logs/strategies/`), and reports (`reports/strategies/`).
- **Aggregation**: `src/risk/aggregator.py` enforces account-level and risk-group-level limits across strategies.
- **Registry**: `config/registry.toml` is the single source of truth. Skills resolve paths via registry lookup, never hardcode.

Full contract: `.claude/rules/multi-strategy.md`.
