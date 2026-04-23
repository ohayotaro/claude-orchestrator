# Codex Delegation Rules

## When to Delegate to Codex CLI

### Design & Architecture
- New class/module design decisions
- Trade logic algorithm design
- Risk model mathematical design
- Data pipeline architecture decisions
- Strategy optimization algorithms

### Code Review
- Strategy code statistical correctness
- MQL5 EA order management logic
- Risk calculation numerical precision
- Performance-critical code paths

### Debugging & Analysis
- Python traceback root cause analysis
- MQL5 compilation error resolution
- Backtest result anomaly analysis
- Data quality issue diagnosis

### Statistical Validation
- Backtest result significance testing
- Overfitting risk quantitative assessment
- Parameter stability analysis
- Walk-forward validation

## Command Templates

### Design Review (interactive)
```bash
codex exec "Review this design: {context}"
```

### Debugging (auto-fix)
```bash
codex exec --full-auto "Debug and fix: {error_context}"
```

### Algorithm Design (interactive)
```bash
codex exec "Design algorithm for: {specification}"
```

### MQL5 Review (interactive)
```bash
codex exec "Review MQL5 EA: {code_context}"
```

## Failure Handling

When a Codex CLI call fails (non-zero exit code, timeout, or empty output):

1. **Notify the user immediately** with:
   - What was being delegated (task description)
   - The error (exit code, stderr, or "empty response")
   - Which skill step was affected
2. **Do NOT silently skip the step** — the delegation was requested because the task requires deep reasoning. Skipping it degrades quality.
3. **Offer alternatives:**
   - Retry the same command
   - Proceed without Codex but flag the result as **unvalidated** (mark clearly in output)
   - User runs Codex interactively in a separate terminal (`! codex "..."`)
4. **Log the failure** — if `/bot-monitor` or structured logging is active, emit a log event.

**Example notification:**
```
Codex delegation failed:
  Task: "Validate backtest results (Sharpe significance)"
  Error: exit code 1 — "rate limit exceeded"
  Skill: /backtest Step 6
  
  Options:
  1. Retry
  2. Continue without Codex validation (result will be marked as unvalidated)
  3. Run manually: ! codex exec "Validate backtest results: ..."
```

## Response Requirements

Codex responses must follow this structure:
1. TL;DR (3 lines max)
2. Analysis (detailed)
3. Plan (implementation steps)
4. Code (if applicable)
5. Validation (verification method)
6. Risks (mandatory)
