# Financial Trading AI Orchestrator

Claude Code (Opus 4.6) をオーケストレーターとし、Codex CLI (GPT-5.4) と Gemini CLI (Gemini 2.5 Pro) を専門エージェントとして統合する金融トレーディングAIチーム。

暗号資産・外為・先物市場のバックテスト解析、トレードロジック開発、EA (Expert Advisor) 開発に特化。

## Architecture

```
┌──────────────────────────────────────────────────────┐
│               Claude Code (Opus 4.6)                 │
│               ── Orchestrator ──                     │
│    Delegates, integrates, does NOT implement         │
├──────────────┬───────────────┬───────────────────────┤
│  Subagents   │   Codex CLI   │     Gemini CLI        │
│  (Opus)      │   (GPT-5.4)   │     (Gemini 2.5 Pro)  │
│              │               │                       │
│  - Codebase  │  - Design     │  - Chart analysis     │
│  - Review    │  - Debug      │  - PDF extraction     │
│  - Docs      │  - Algorithm  │  - Research           │
│  - Tests     │  - Statistics  │  - Visualization      │
└──────────────┴───────────────┴───────────────────────┘
```

### Routing Policy

| AI | Role | Trigger |
|----|------|---------|
| **Claude Subagents** | Codebase exploration, lightweight review, docs, tests | 3+ files to read, documentation tasks |
| **Codex CLI** | Algorithm design, statistical validation, MQL5 review, debugging | Design decisions, errors, complex logic |
| **Gemini CLI** | Chart pattern recognition, PDF parsing, multimodal research | Image/PDF input, visual analysis |

## Specialized Team Agents

| Agent | Domain | File Scope |
|-------|--------|------------|
| `data-engineer` | Market data pipelines (Binance, bybit, MT5, yfinance) | `src/data/*` |
| `quant-analyst` | Backtesting, statistics, risk management | `src/backtesting/*`, `src/risk/*` |
| `strategist` | Trade logic design, signal generation | `src/strategies/*` |
| `ea-developer` | MQL5 Expert Advisors, Python bots | `mql5/*` |
| `codex-debugger` | Error analysis via Codex CLI | Any (error routing) |

## Skill Pipeline

```
/data-pipeline → /strategy-design → /backtest → /optimize → /ea-generate
     │                  │               │            │            │
  Fetch data      Design logic     Validate     Tune params   Convert to
  Clean/store     Define signals   Measure      Walk-forward  MQL5 EA
                  Set rules        Report       Monte Carlo   Deploy
```

### Available Skills (13)

| Skill | Description |
|-------|-------------|
| `/init-finance` | Initialize project structure, dependencies, and config |
| `/data-pipeline` | Build market data acquisition and storage pipelines |
| `/backtest` | Execute backtests with performance metrics and Codex validation |
| `/strategy-design` | Design new strategies with parallel Researcher/Strategist analysis |
| `/optimize` | Walk-forward optimization with overfitting detection |
| `/ea-generate` | Convert Python strategies to MQL5 Expert Advisors |
| `/market-analysis` | Multi-timeframe analysis with Gemini chart recognition |
| `/risk-report` | Portfolio risk assessment (VaR/CVaR, stress testing) |
| `/team-implement` | Parallel implementation via Agent Teams |
| `/team-review` | 3-reviewer parallel code review (Security, Quant, Performance) |
| `/codex-system` | Direct Codex CLI delegation templates |
| `/gemini-system` | Direct Gemini CLI delegation templates |
| `/checkpointing` | Session state snapshot and recovery |

## Hooks (8)

Hooks enforce routing policies at the tool-call level:

| Hook | Event | Purpose |
|------|-------|---------|
| `agent-router.py` | UserPromptSubmit | Analyze prompt and suggest optimal AI routing |
| `check-codex-before-write.py` | PreToolUse (Edit/Write) | Flag design decisions for Codex review |
| `suggest-gemini-research.py` | PreToolUse (WebSearch/WebFetch) | Suggest Gemini for research tasks |
| `error-to-codex.py` | PostToolUse (Bash) | Route errors to codex-debugger |
| `post-backtest-analysis.py` | PostToolUse (Bash) | Auto-analyze backtest results |
| `post-implementation-review.py` | PostToolUse (Edit/Write) | Suggest Codex review after large changes |
| `lint-on-save.py` | PostToolUse (Edit/Write) | Auto-lint Python/MQL5 files |
| `log-cli-tools.py` | PostToolUse (Bash) | Log Codex/Gemini CLI usage |

## Rules (8)

| Rule | Scope |
|------|-------|
| `financial-domain.md` | Numerical precision, backtest principles, data quality |
| `risk-management.md` | Position limits, loss limits, emergency stop requirements |
| `security.md` | API key management, testnet-first, no hardcoded secrets |
| `codex-delegation.md` | When and how to delegate to Codex CLI |
| `gemini-delegation.md` | When and how to delegate to Gemini CLI |
| `coding-principles.md` | Type hints, testing, naming conventions (Python/MQL5) |
| `testing.md` | Test categories, pytest conventions, markers |
| `language.md` | Japanese for users, English for code/agents |

## Prerequisites

- [Claude Code](https://claude.ai/code) (CLI)
- [Codex CLI](https://github.com/openai/codex) (`brew install codex` or `npm i -g @openai/codex`)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli) (`npm i -g @anthropic-ai/gemini-cli`)
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

## Quick Start

```bash
# Clone
git clone https://github.com/ohayotaro/claude-orchestrator.git
cd claude-orchestrator

# Set up environment
cp .env.example .env
# Edit .env with your API keys (Binance, bybit, MT5, etc.)

# Install Python dependencies
uv sync

# Start Claude Code in this directory
claude

# Initialize the project (within Claude Code)
/init-finance
```

## Usage Examples

```bash
# Within Claude Code session:

# Build a data pipeline for BTC/USDT
/data-pipeline

# Design a moving average crossover strategy
/strategy-design

# Run a backtest with statistical validation
/backtest

# Optimize strategy parameters
/optimize

# Generate MQL5 Expert Advisor
/ea-generate

# Analyze current market conditions
/market-analysis

# Generate risk report
/risk-report

# Delegate to Codex for deep analysis
/codex-system Review this algorithm for overfitting risk

# Delegate to Gemini for chart analysis
/gemini-system Analyze chart patterns in chart.png
```

## Project Structure

```
claude-orchestrator/
├── CLAUDE.md                    # 3-zone orchestrator contract
├── .claude/
│   ├── settings.json            # Hooks, permissions, env vars
│   ├── agents/                  # 6 specialized subagent definitions
│   ├── hooks/                   # 8 Python hook scripts
│   ├── rules/                   # 8 domain rule files
│   ├── skills/                  # 13 skill definitions (SKILL.md)
│   └── docs/                    # DESIGN.md, CODEX_HANDOFF_PLAYBOOK.md
├── .codex/
│   ├── AGENTS.md                # Codex agent contract
│   └── config.toml              # Codex CLI config (GPT-5.4)
├── .gemini/
│   ├── GEMINI.md                # Gemini agent contract
│   └── settings.json            # Gemini CLI config (Gemini 2.5 Pro)
├── src/
│   ├── data/                    # Data fetching and management
│   ├── strategies/              # Trading strategies
│   ├── backtesting/             # Backtest engine
│   ├── optimization/            # Parameter optimization
│   ├── risk/                    # Risk management
│   └── utils/                   # Utilities
├── mql5/
│   ├── experts/                 # Expert Advisors
│   ├── include/                 # Shared MQL5 libraries
│   └── indicators/              # Custom indicators
├── tests/                       # Test suite
├── data/                        # Data storage (gitignored)
├── reports/                     # Backtest reports output
└── pyproject.toml               # Python dependencies (uv)
```

## CLAUDE.md — 3-Zone Architecture

| Zone | Content | Mutability |
|------|---------|------------|
| **Zone A** | Orchestration rules, routing policy, delegation triggers | Immutable template |
| **Zone B** | Project identity, tech stack, key commands | Set by `/init-finance` |
| **Zone C** | Active work context, current decisions | Dynamic (updated per session) |

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Analysis & Backtesting | Python 3.11+, backtrader, vectorbt, pandas, numpy |
| EA Development | MQL5 (MetaTrader 5) |
| Data Sources | Binance API, bybit API, MT5 API, yfinance |
| Orchestrator | Claude Code (Opus 4.6, 1M context) |
| Deep Reasoning | Codex CLI (GPT-5.4) |
| Multimodal | Gemini CLI (Gemini 2.5 Pro) |
| Package Manager | uv |
| Linter | ruff |
| Type Checker | mypy |
| Testing | pytest |

## References

- [claude-code-orchestra](https://github.com/DeL-TaiseiOzaki/claude-code-orchestra) — Multi-AI orchestration template
- [everything-claude-code](https://github.com/affaan-m/everything-claude-code) — Cross-harness plugin framework

## License

MIT
