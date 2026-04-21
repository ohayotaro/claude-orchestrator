---
name: checkpointing
description: Save current session state including git status, progress, and context as a snapshot for session recovery and handoff.
allowed-tools: "Bash(git *) Bash(ls *) Read Write Glob"
---

# Session Checkpointing

Capture a full snapshot of the current session state.

## Workflow

### Step 1: Capture Git State
```bash
git status
git log --oneline -10
git diff --stat
```

### Step 2: Capture Active Context
- Read current Zone C of CLAUDE.md
- List recently modified files
- Check for uncommitted changes

### Step 3: Save Checkpoint
Write checkpoint file to `.claude/checkpoints/{timestamp}.md`:

```markdown
# Checkpoint: {timestamp}

## Git State
- Branch: {branch}
- Last commit: {hash} {message}
- Uncommitted changes: {list}

## Active Work
- Current task: {description}
- Files in progress: {list}
- Pending decisions: {list}

## Context
- Strategies being developed: {list}
- Data pipelines active: {list}
- Recent backtest results: {summary}

## Agent Activity
- Codex delegations: {count}
- Gemini delegations: {count}
- Subagent tasks: {count}

## Next Steps
- {recommended next actions}
```

### Step 4: Discover Reusable Patterns
Scan session history for patterns that should be extracted:
- Common code patterns → candidate for `src/utils/`
- Repeated commands → candidate for skill or command
- Frequent delegations → candidate for hook optimization

### Step 5: Update Zone C
Append checkpoint summary to CLAUDE.md Zone C for cross-session persistence.
If Zone C exceeds 50 lines, summarize older entries and trim.

### Step 6: Document Staleness Check
Review per `document-lifecycle.md` rules:
- [ ] CLAUDE.md Zone C: >50 lines? → Summarize
- [ ] DESIGN.md: Updated since last structural code change?
- [ ] api_specs/: Any spec >6 months old? → Flag for re-research
- [ ] CODEX_HANDOFF_PLAYBOOK.md: New skills added since last update? → Flag

Report any stale documents to the user with recommended action.
