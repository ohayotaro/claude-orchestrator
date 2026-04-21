---
name: codex-system
description: Execute deep reasoning tasks via Codex CLI. Provides templates for design review, debugging, algorithm design, and MQL5 review.
disable-model-invocation: true
allowed-tools: "Bash(codex *) Read Write"
---

# Codex CLI Integration

Delegate deep reasoning tasks to Codex CLI (GPT-5.4).

## Usage

Invoke with `/codex-system` followed by the task type.

## Task Templates

### Design Review
```bash
codex -a on-request "Review this design:
$ARGUMENTS

Evaluate:
1. Correctness and completeness
2. Edge cases and failure modes
3. Scalability and performance
4. Financial domain accuracy
5. Risk control adequacy"
```

### Debugging
```bash
codex --full-auto "Debug and fix this error:
$ARGUMENTS

Identify root cause, propose fix, suggest regression test."
```

### Algorithm Design
```bash
codex -a on-request "Design an algorithm for:
$ARGUMENTS

Requirements:
- Must handle large datasets efficiently
- Must maintain financial calculation precision
- Provide complexity analysis
- Include test strategy"
```

### MQL5 Review
```bash
codex -a on-request "Review this MQL5 code:
$ARGUMENTS

Check:
1. Order management (CTrade, error handling)
2. Memory management (ArrayFree, handles)
3. Error handling (GetLastError)
4. Risk controls (SL/TP, lot sizing)"
```

### Statistical Validation
```bash
codex -a on-request "Statistically validate:
$ARGUMENTS

Perform:
1. Significance testing
2. Confidence interval estimation
3. Overfitting risk assessment
4. Robustness analysis"
```

## Notes
- Use `-a on-request` for interactive review (default)
- Use `--full-auto` for auto-fix tasks (debugging, simple fixes)
- Always include relevant context (code, metrics, error messages)
- See `.claude/docs/CODEX_HANDOFF_PLAYBOOK.md` for detailed templates
