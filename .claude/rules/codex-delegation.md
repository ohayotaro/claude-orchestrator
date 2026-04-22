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

## Response Requirements

Codex responses must follow this structure:
1. TL;DR (3 lines max)
2. Analysis (detailed)
3. Plan (implementation steps)
4. Code (if applicable)
5. Validation (verification method)
6. Risks (mandatory)
