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

### Step 6: Checkpoint Commit
Create a git commit to preserve the checkpoint state. This is separate from feature commits.

```bash
git add CLAUDE.md .claude/checkpoints/ .claude/docs/ reports/
git commit -m "chore(checkpoint): session snapshot {timestamp}

Checkpoint includes:
- Zone C context update
- {summary of drift detection results, if any}
- {summary of document updates, if any}

[checkpoint — not a feature commit]"
```

Rules:
- **Only commit orchestrator state files** (CLAUDE.md, checkpoints/, docs/, reports/). Do NOT commit uncommitted source code — that is the user's responsibility.
- **Use `chore(checkpoint):` prefix** to distinguish from feature/fix commits in git log.
- **Ask the user before committing** if there are staged source code changes that might be unintentionally included. Run `git status` first.
- If the user declines the commit, the checkpoint file is still saved locally but not in git history.

### Step 7: Document Drift Detection
Run each check defined in `document-lifecycle.md` "Drift Detection" section:

1. **Zone C Overload**: Count lines in Zone C. If >50, summarize old entries and trim.
2. **DESIGN.md Divergence**: Run `git log --since=<DESIGN.md mtime> -- src/ mql5/` — if commits added/removed modules not in DESIGN.md, list the mismatches.
3. **api_specs/ Mismatch**: For each spec file, grep the corresponding client code for base URL and endpoint paths. Flag if they differ from the spec.
4. **Playbook Gaps**: List skills that use `codex` in their SKILL.md but have no section in CODEX_HANDOFF_PLAYBOOK.md.
5. **Routing Gaps**: Compare agent names in `.claude/agents/` with keys in `routing-keywords.json`. Flag missing or orphaned entries.

Report each detected issue to the user with:
- **What**: Which document is out of sync
- **Why**: What changed in code/config that the document doesn't reflect
- **Action**: Specific fix (update ADR, re-research API, add playbook template, etc.)
