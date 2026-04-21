# Architecture Design Document

## System Overview

This project is an AI-orchestrated financial trading system that coordinates three AI agents:

```
┌─────────────────────────────────────────────────┐
│              Claude Code (Opus 4.6)              │
│              ── Orchestrator ──                  │
│  Delegates, integrates, does NOT implement       │
├─────────────┬─────────────┬─────────────────────┤
│  Subagents  │  Codex CLI  │    Gemini CLI       │
│  (Opus)     │  (GPT-5.4)  │    (Gemini 2.5 Pro) │
│             │             │                     │
│ - Codebase  │ - Design    │ - Chart analysis    │
│ - Review    │ - Debug     │ - PDF extraction    │
│ - Docs      │ - Algorithm │ - Research          │
│ - Tests     │ - Stats     │ - Visualization     │
└─────────────┴─────────────┴─────────────────────┘
```

## Specialized Team Agents

| Agent | Domain | File Scope |
|-------|--------|------------|
| data-engineer | Data pipelines | src/data/* |
| quant-analyst | Backtesting, statistics, risk | src/backtesting/*, src/risk/* |
| strategist | Trade logic, signals | src/strategies/* |
| ea-developer | MQL5 EA, Python bots | mql5/* |
| codex-debugger | Error analysis | (any — via Codex CLI) |

## Skill Pipeline

```
/data-pipeline → /strategy-design → /backtest → /optimize → /ea-generate
     │                  │               │            │            │
  Fetch data      Design logic     Validate     Tune params   Convert to
  Clean/store     Define signals   Measure      Walk-forward  MQL5 EA
                  Set rules        Report       Monte Carlo   Deploy
```

## Architecture Decisions

### ADR-001: Orchestrator Pattern
- **Decision**: Claude Code delegates, does not implement
- **Rationale**: Conserve 1M context for coordination; leverage specialized models

### ADR-002: Dual Language Stack
- **Decision**: Python for analysis/backtesting, MQL5 for EA execution
- **Rationale**: Python has superior data science ecosystem; MQL5 is required for MetaTrader

### ADR-003: Data Format
- **Decision**: Parquet for storage, DataFrame for processing
- **Rationale**: Parquet offers columnar compression and fast I/O; pandas/polars interop

### ADR-004: Hook-Driven Routing
- **Decision**: Python hooks intercept tool calls to suggest AI routing
- **Rationale**: Enforcement at tool-call level is more reliable than prompt instructions alone
