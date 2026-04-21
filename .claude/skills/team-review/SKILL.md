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
- **Look-ahead bias detection** (see checklist below)
- Edge cases (zero division, empty data, NaN handling)
- Risk management completeness

**Look-ahead bias checklist** (Quant Reviewer must verify each):
1. **Signal shift**: Are trading signals shifted by at least 1 bar before use? (`signal.shift(1)` or equivalent). Entry at bar N must use only data from bar N-1 and earlier.
2. **Non-causal indicators**: Are any indicators computed with future data? (centered moving averages, forward-looking smoothing, bilateral filters). These are valid only as oracle/ground-truth labels, never as live signals.
3. **Train/test leakage**: For ML models, is there a purge gap >= prediction horizon between training and test data? Is an embargo period applied after the purge?
4. **Label leakage**: Are ground-truth / oracle labels (RAPR, trend scanning, centered MA) used only for training, never accessible during test/live inference?
5. **Label mapping from train only**: If labels are remapped (e.g., HMM state → BULL/BEAR), is the mapping built exclusively from training data and then applied to test data?
6. **Feature computation scope**: Are features computed only from past data at each point? Check for `rolling()` with `center=True`, or any operation that implicitly uses future rows.
7. **Data alignment**: When merging multiple timeframes, is the lower-timeframe data aligned to the higher-timeframe bar's **close time** (not open time), preventing access to incomplete bars?

**Live Reproducibility Reviewer** (quant-analyst or bot-engineer, depending on scope):
Applies to strategy code, backtest engine, data pipeline, AND bot code — not just bots.
- Backtest/live parity: will the same signal logic produce the same decisions with live data? (incomplete bars, delayed data, warm-up period)
- Execution assumptions: does the backtest assume instant fills, zero slippage, or unlimited liquidity that won't hold live?
- Non-determinism handling: network latency, partial fills, slippage, rate limit waits — are these accounted for or assumed away?
- Timestamp consistency: are all time comparisons using the same source (exchange time vs local time vs UTC)?
- Data source divergence: does the live system use the same data format and source as the backtest? (historical API vs WebSocket, adjusted vs raw prices)
- State recovery (bot code): if the process crashes mid-trade, does it restore correctly from persisted state?
- Logging contract compliance (bot code): are all mandatory events from `bot-development.md` Structured Logging Contract emitted?

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
