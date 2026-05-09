# Finance AI Orchestrator

> Claude Code (Opus 4.7, 1M context) as orchestrator, coordinating Codex CLI and Gemini CLI as specialized agents for a financial trading AI team. Markets-agnostic — crypto / FX / futures / equities, with optional MQL5 EA generation.

```
Claude Code (Orchestrator) ─┬─ Codex CLI       (algorithm design, statistical validation, risk modeling)
                             ├─ Gemini CLI      (chart / PDF / IR-report multimodal extraction)
                             └─ Opus subagents  (data, strategy, EA, bot, ML, infra, debug, docs)
```

- **9 role-based agents** (data-engineer, quant-analyst, strategist, ea-developer, bot-engineer, infra-ops, ml-engineer, codex-debugger, general-purpose)
- **24 skills** spanning data pipeline, strategy design, backtest, optimization, MQL5 EA generation, bot development / deployment / monitoring, ML pipelines, equity research, IR analysis, risk reporting, and incident response
- **12 rules** covering financial domain (no look-ahead bias, mandatory transaction costs, OOS testing), risk management (mandatory stops, layered safety gates, circuit breakers), security, deployment, monitoring, plus delegation protocols for Codex and Gemini
- **9 hooks** including `agent-router` (single primary + optional fallback), `check-codex-before-write`, `post-backtest-analysis` (threshold check + failure-aware), `post-bot-execution`, `error-to-codex`, `lint-on-save`, `log-cli-tools`, `suggest-gemini-research`, `post-implementation-review`
- **Markets-agnostic via `/init-finance`**: target market, data sources, backtest framework, execution platform, and tooling all chosen at init time and recorded in CLAUDE.md Zone B

## Quick start

Install prerequisites first (see [Prerequisites](#prerequisites)). Then, in your trading-project directory:

```bash
cd /path/to/your-trading-project
git clone --depth 1 https://github.com/ohayotaro/claude-finance.git .starter \
  && cp -r .starter/.claude .starter/.codex .starter/.gemini .starter/CLAUDE.md . \
  && rm -rf .starter
claude
```

Inside Claude Code:

```
/init-finance     # markets / data sources / backtest framework / execution platform wizard
```

After the wizard, `CLAUDE.md` Zone B describes your stack and the financial domain rules are activated.

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Claude Code | latest | `npm i -g @anthropic-ai/claude-code` |
| Codex CLI | ≥0.121 | `brew install codex` (macOS) or `npm i -g @openai/codex` |
| Gemini CLI | ≥0.38 | `npm i -g @google/gemini-cli` |
| Git | any | system package manager |
| Python | ≥3.11 | for hooks (`.claude/hooks/*.py`) |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

After install:

```bash
claude --version
codex --version  && codex login
gemini --version && gemini login
```

## What gets copied into your project

```
your-trading-project/
├── CLAUDE.md                       # 3-Zone orchestrator contract
├── .claude/
│   ├── settings.json               # hooks + env + permission allowlist
│   ├── agents/                     # 9 role-based Opus subagents
│   ├── hooks/                      # 9 Python hooks
│   ├── rules/                      # 12 domain rules
│   ├── skills/                     # 24 skill definitions
│   ├── routing-keywords.json       # routing config (customizable)
│   ├── backtest-thresholds.json    # threshold config (customizable)
│   └── docs/                       # DESIGN, CODEX_HANDOFF_PLAYBOOK, reviews/
├── .codex/                         # Codex CLI contract + config
└── .gemini/                        # Gemini CLI contract + config
```

Your project code (`src/`, `mql5/`, `tests/`, `data/`, etc.) is left alone. The template owns nothing outside the four targets above.

## Workflow

```
Strategy:    /data-pipeline → /strategy-design → /backtest → /optimize ─┬→ /ea-generate
                                                                         └→ /bot-develop → /bot-deploy → /bot-monitor
ML:          /data-pipeline → /ml-pipeline → /backtest → /optimize → /bot-develop
Equity:      /equity-screener → /earnings-calendar → /sector-analysis → /ir-analysis → /strategy-design
Risk & ops:  /risk-report, /team-review, /incident-response, /checkpointing
```

See `.claude/docs/DESIGN.md` for the full architecture, routing policy, and rationale.

## Skills

24 skills organized by purpose. Full spec for each is at `.claude/skills/<name>/SKILL.md`. The "Owner" column lists the agent or external CLI that performs the heavy work; the orchestrator drives the flow but does not implement.

### Setup

| Skill | Purpose | Owner |
|---|---|---|
| `/init-finance` | Project init wizard — markets, data sources, backtest framework, execution platform; populates CLAUDE.md Zone B and scaffolds `src/`, `mql5/`, `tests/`. | — |
| `/checkpointing` | Zone C snapshot + 5 drift checks (Zone C overload, DESIGN.md vs code, api_specs/ version, playbook gaps, routing-keywords vs agents). Checkpoint files are local-only; only durable state (CLAUDE.md, docs/, reports/) is committed. | — |

### Strategy pipeline

| Skill | Purpose | Owner |
|---|---|---|
| `/data-pipeline` | Market-data fetch / normalize / Parquet store. Mandatory API spec research before client code. | data-engineer |
| `/strategy-design` | Parallel Researcher / Strategist / Gemini analysis → Codex algorithm review → strategy spec. | strategist + Codex |
| `/backtest` | Backtest run with IS/OOS split, Codex statistical validation (Sharpe p-value, bootstrap CI), optional Gemini chart interpretation. | quant-analyst + Codex |
| `/optimize` | Walk-forward optimization with Optuna, overfitting detection, Monte Carlo robustness. | quant-analyst + Codex |
| `/market-analysis` | Multi-timeframe analysis with Gemini chart pattern recognition. | Gemini |

### Equity research

| Skill | Purpose | Owner |
|---|---|---|
| `/equity-screener` | Fundamental + technical screening (PER / PBR / ROE, growth, sector filters). | quant-analyst + Codex |
| `/earnings-calendar` | Earnings dates, dividends, corporate actions for event-driven strategies. | data-engineer |
| `/sector-analysis` | Sector performance comparison, rotation signals, cross-sector correlation. | quant-analyst + Codex |
| `/ir-analysis` | Investor-focused report from IR materials (annual reports, calls, ESG) — Gemini PDF extraction + Codex synthesis. | Codex + Gemini |

### Bot & EA

| Skill | Purpose | Owner |
|---|---|---|
| `/ea-generate` | Python strategy → MQL5 Expert Advisor conversion with Codex code review. | ea-developer + Codex |
| `/bot-develop` | API bot (ccxt / WebSocket / asyncio) with order state machine, structured logging contract, testnet validation. | bot-engineer + Codex |
| `/bot-deploy` | Docker / systemd / launchd deployment, health checks, env-var secret management. | infra-ops + Codex |
| `/bot-monitor` | Structured logging, core metrics (uptime, PnL, latency, errors), alert thresholds, notification channels. | infra-ops |

### ML

| Skill | Purpose | Owner |
|---|---|---|
| `/ml-pipeline` | Feature engineering → walk-forward (purge / embargo) → Optuna HPO → overfitting detection → ablation. | ml-engineer + Codex |

### Quality & risk

| Skill | Purpose | Owner |
|---|---|---|
| `/team-review` | 4-track parallel review — Security, Quant, Live Reproducibility, Performance — with Codex final judgment. | Codex per track |
| `/risk-report` | VaR / CVaR, stress testing, correlation analysis, Codex model validation. | quant-analyst + Codex |

### Operations

| Skill | Purpose | Owner |
|---|---|---|
| `/incident-response` | Trading bot incident handling — emergency stop → root cause (Codex) → recovery → postmortem. | Codex + relevant agents |
| `/dashboard-develop` | Use-case-specific dashboards (bot monitoring / backtest / portfolio / research). Python-only stack (Streamlit / Dash / FastAPI + Jinja2 / Grafana). | infra-ops |
| `/notification-setup` | Bot log events → notification channel routing design. | bot-engineer |
| `/team-implement` | Agent Teams parallel implementation across disjoint file scopes per role. | role-specific agents |

### Adapters

| Skill | Purpose | Owner |
|---|---|---|
| `/codex-system` | One-off Codex consultation. | Codex |
| `/gemini-system` | One-off Gemini multimodal task. | Gemini |

## Updating the template

Run `scripts/update.sh` from your project root to refresh the template. It backs up Zone B and customizable JSON, pulls the latest, then restores the backups.

```bash
cd /path/to/your-trading-project
bash <(curl -fsSL https://raw.githubusercontent.com/ohayotaro/claude-finance/main/scripts/update.sh)
```

Or, if `scripts/update.sh` is already in your tree:

```bash
./scripts/update.sh
```

Preserved: `CLAUDE.md` Zone B, `.claude/routing-keywords.json`, `.claude/backtest-thresholds.json`, `.claude/settings.local.json`.

Overwritten: `.claude/` agents / hooks / rules / skills / settings.json, `.codex/`, `.gemini/`, `CLAUDE.md` Zone A. Untouched: project code (`src/`, `mql5/`, `tests/`), `pyproject.toml`, `README.md`.

## Architecture

```
┌────────────────────────────────────────────────────────┐
│      Claude Code (Opus 4.7, 1M)  — Orchestrator        │
├──────────────────┬──────────────┬──────────────────────┤
│  Opus Subagents  │  Codex CLI    │  Gemini CLI          │
│ codebase work    │ algorithm     │ chart pattern        │
│ implementation   │ statistics    │ PDF / IR reports     │
│ review / docs    │ debugging     │ multimodal research  │
│ parallel teams   │ risk modeling │ visualization        │
└──────────────────┴──────────────┴──────────────────────┘
```

- **Codex** receives English-only structured prompts (templates in `.claude/docs/CODEX_HANDOFF_PLAYBOOK.md` covering strategy review, backtest validation, MQL5 review, error analysis, optimization, risk modeling, team-review, incident postmortem, IR synthesis, equity screening, sector rotation, optimization validation, ML validation) and returns the standard contract: TL;DR → Analysis → Plan → Validation → Risks → Confidence.
- **Gemini** receives multimodal input (charts, PDFs, screenshots) and returns structured Markdown with confidence ratings (High / Medium / Low) per item.
- **Opus subagents** are role-named, market-agnostic, and read CLAUDE.md Zone B at runtime.

The orchestration contract is enforced at the hook layer: `agent-router` selects a single primary route plus optional fallback (rather than dumping every keyword match), `check-codex-before-write` warns on design-touching edits, `post-backtest-analysis` checks thresholds and emits failure context on non-zero exit code, `post-implementation-review` counts net additions to avoid noisy reviews on repeated edits, `post-bot-execution` detects bot errors and connection drops, plus four more.

### Configuration files

| File | Purpose | Fallback |
|---|---|---|
| `.claude/routing-keywords.json` | Hook routing keywords per agent | built-in defaults |
| `.claude/backtest-thresholds.json` | Per-metric warning thresholds | built-in defaults |
| `.claude/settings.json` | Hooks, permissions, env vars | — |
| `.codex/config.toml` | Codex CLI model + flags | — |
| `.gemini/settings.json` | Gemini CLI model + flags | — |

## CLAUDE.md — 3-Zone architecture

| Zone | Contents | Update policy |
|------|----------|---------------|
| **A** (above `@orchestra:template-boundary`) | Orchestration rules, routing policy, delegation triggers, quality gates, language protocol | Stable. Updated only by template version bump |
| **B** (between the two boundary markers) | Project-specific config: markets, data sources, execution platform, key commands | Set by `/init-finance`. Manually editable |
| **C** (below `@orchestra:repo-boundary`) | Active work context, design decisions log | Updated dynamically per session; trimmed by `/checkpointing` when >50 lines |

## Language protocol

| Channel | Language |
|---|---|
| Orchestrator ↔ User | Japanese (default) |
| Agent ↔ Agent / Codex / Gemini | English (fixed) |
| Code / commit messages / docs | English (fixed) |

## Provenance

Financial-trading specialization. The full-stack web/mobile sibling is at [`ohayotaro/claude-fullstack-orchestrator`](https://github.com/ohayotaro/claude-fullstack-orchestrator). Both draw structural cues from [`DeL-TaiseiOzaki/claude-code-orchestra`](https://github.com/DeL-TaiseiOzaki/claude-code-orchestra) (multi-agent dev environment) and the rules layout pattern from [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code). Meta-design reviewed by Codex CLI on 2026-05-09 (record at `.claude/docs/reviews/codex-meta-review-2026-05-09.md`).

## License

MIT
