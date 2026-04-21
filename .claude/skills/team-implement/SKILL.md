---
name: team-implement
description: Parallel implementation using Agent Teams. Each team member works on independent file sets to avoid conflicts.
allowed-tools: "Bash(python *) Bash(uv *) Bash(pytest *) Read Write Edit Glob Grep"
---

# Team Parallel Implementation

Distribute implementation work across specialized agent team members.

## Workflow

### Step 1: Task Decomposition
Break the implementation into independent modules:
- Identify file ownership boundaries
- Ensure no file is owned by multiple agents
- Define interfaces between modules

### Step 2: Agent Assignment

| Agent | File Scope | Responsibility |
|-------|-----------|----------------|
| data-engineer | `src/data/*` | Data fetching, cleaning, storage |
| quant-analyst | `src/backtesting/*`, `src/risk/*` | Backtest engine, risk calculations |
| strategist | `src/strategies/*` | Strategy logic, signals |
| ea-developer | `mql5/*` | Expert Advisors, MQL5 code |
| general-purpose | `src/utils/*`, `tests/*` | Utilities, test code |

### Step 3: Parallel Execution
Launch Agent Teams with each member assigned their file set:
- Each member MUST only edit files within their assigned scope
- Members write work logs to `.claude/logs/agent-teams/`
- Members check shared task list for dependencies

### Step 4: Interface Verification
After parallel work completes:
- Verify module interfaces match (imports, function signatures)
- Check for type consistency across module boundaries
- Run mypy for cross-module type checking

### Step 5: Integration
- Merge all changes
- Resolve any remaining interface mismatches
- Run full test suite: `uv run pytest`

### Step 6: Quality Check
- Run linter: `uv run ruff check src/`
- Run type checker: `uv run mypy src/`
- Verify no files were edited outside assigned scope
