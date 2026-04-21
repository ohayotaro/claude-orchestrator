---
name: team-review
description: Parallel code review with 4 specialist reviewers (Security, Quant, Live Reproducibility, Performance) and Codex final judgment.
allowed-tools: "Bash(python *) Bash(codex *) Bash(git *) Read Glob Grep"
---

# Team Code Review

Comprehensive parallel code review by specialized reviewers.

## Workflow

### Step 1: Identify Review Scope
- List changed files (via `git diff` or explicit list)
- Categorize changes by domain

### Step 2: Launch Parallel Reviewers

**Security Reviewer** (general-purpose):
- API key management (no hardcoded secrets)
- Input validation and sanitization
- Authentication and authorization patterns
- Injection vulnerabilities
- Sensitive data in logs or error messages

**Quant Reviewer** (quant-analyst):
- Calculation precision (floating-point issues)
- Statistical correctness (formula validation)
- Look-ahead bias detection
- Edge cases (zero division, empty data, NaN handling)
- Risk management completeness

**Live Reproducibility Reviewer** (bot-engineer):
- Backtest/live parity: will the same signal logic produce the same decisions in both environments?
- Non-determinism handling: network latency, partial fills, slippage, rate limit waits — are these accounted for or assumed away?
- Timestamp consistency: are all time comparisons using the same source (exchange time vs local time vs UTC)?
- State recovery: if the bot crashes mid-trade, does it restore correctly from persisted state?
- Data source divergence: does the bot use the same data feed as the backtest, or a different one (WebSocket vs REST, real-time vs delayed)?
- Logging contract compliance: are all mandatory events from `bot-development.md` Structured Logging Contract emitted?

**Performance Reviewer** (general-purpose):
- Execution efficiency (vectorization, unnecessary loops)
- Memory usage (large DataFrame operations)
- I/O optimization (Parquet read/write patterns)
- Scalability (will this work with 1M+ rows?)

### Step 3: Aggregate Findings
Collect and deduplicate issues from all three reviewers:
- Critical: Must fix before merge
- Warning: Should fix, but not blocking
- Info: Suggestions for improvement

### Step 4: Codex Final Judgment
Send aggregated findings to Codex for holistic assessment:
```bash
codex -a on-request "Final code review judgment:
Changes: {file_list}
Security findings: {security_issues}
Quant findings: {quant_issues}
Live reproducibility findings: {repro_issues}
Performance findings: {perf_issues}

Provide: overall assessment, prioritized fix list, risk level (Low/Medium/High)"
```

### Step 5: Output
Generate review report:
- Issue count by severity (Critical/Warning/Info)
- Issue list with file, line, description, suggested fix
- Overall risk assessment
- Approval recommendation (Approve / Request Changes / Block)
