# Document Lifecycle Rules

All persistent documents in this project have defined update triggers. No document should become stale without an explicit decision to archive or remove it.

## Document Registry

### CLAUDE.md

| Zone | Update Trigger | Responsible | Method |
|------|---------------|-------------|--------|
| **Zone A** (template rules) | Template version upgrade only | Template maintainer | Manual or `Section 9.2` update procedure |
| **Zone B** (project identity) | `/init-finance` (initial), or when project scope changes (new market, new data source, new platform) | User or orchestrator | Edit Zone B directly. Must update when: new exchange added, tech stack changed, key commands changed |
| **Zone C** (working context) | Every significant decision, architecture change, or strategy addition | Orchestrator | Append. Triggers: (1) `/strategy-design` completes, (2) `/bot-develop` architecture finalized, (3) major refactor, (4) `/checkpointing` |

**Zone C staleness rule**: If Zone C exceeds 50 lines, the orchestrator should summarize and trim older entries on next `/checkpointing` call.

### .claude/docs/DESIGN.md

| Event | Action |
|-------|--------|
| New agent/skill/module added | Add architecture decision record (ADR) |
| Architecture pattern changed | Update relevant ADR |
| `/strategy-design` produces new architecture | Append strategy architecture summary |
| `/bot-develop` finalizes bot architecture | Append bot component diagram |
| `/team-review` identifies architecture issues | Update with resolution |

**Ownership**: Orchestrator updates after any structural change. Codex reviews for consistency.

### .claude/docs/CODEX_HANDOFF_PLAYBOOK.md

| Event | Action |
|-------|--------|
| New Codex delegation pattern discovered | Add new template section |
| Existing template produces poor results | Revise template with improved prompt |
| New skill with Codex integration added | Add corresponding handoff template |

**Ownership**: Updated when a Codex delegation succeeds or fails in a notable way.

### MEMORY.md (Claude Code auto memory)

This file is managed by Claude Code's auto memory system. Project-specific guidance:

| What to save | What NOT to save |
|---|---|
| User preferences for analysis style | Code patterns (derive from code) |
| Non-obvious project constraints | Git history (use git log) |
| Validated approach decisions | Ephemeral task state |
| External resource locations | Anything in CLAUDE.md or DESIGN.md |

**Rule**: Do not duplicate information that exists in CLAUDE.md Zone B/C or DESIGN.md.

### reports/ (Backtest, Risk, IR)

| Document | Created by | Retention |
|----------|-----------|-----------|
| `reports/backtest_*.html` | `/backtest` | Keep all. Compare across strategy versions |
| `reports/ir/{company}_*.md` | `/ir-analysis` | Keep all. Dated for historical reference |
| `reports/risk_*.md` | `/risk-report` | Keep latest + archive previous |

### .claude/docs/incidents/

| Document | Created by | Retention |
|----------|-----------|-----------|
| `incidents/{date}_{title}.md` | `/incident-response` | Keep all. Postmortems are permanent records |

### src/data/api_specs/

| Document | Created by | Update Trigger |
|----------|-----------|---------------|
| `api_specs/{source}.md` | `/data-pipeline` Step 2, `/bot-develop` Step 2 | When API version changes, endpoint deprecation, or rate limit change detected |

**Staleness check**: Before implementing against an existing api_spec, verify the documented API version matches the current version. If >6 months old, re-research.

## Automatic Update Points

These events SHOULD trigger document updates (enforced by skill workflows and orchestrator awareness):

```
/init-finance          → CLAUDE.md Zone B (create)
/strategy-design       → CLAUDE.md Zone C (append), DESIGN.md (ADR if new pattern)
/bot-develop           → CLAUDE.md Zone C (append), DESIGN.md (bot architecture)
/backtest              → reports/ (create)
/optimize              → reports/ (create), CLAUDE.md Zone C (best params)
/ea-generate           → DESIGN.md (EA architecture)
/ir-analysis           → reports/ir/ (create)
/risk-report           → reports/ (create)
/incident-response     → .claude/docs/incidents/ (create)
/checkpointing         → CLAUDE.md Zone C (summarize + trim)
/data-pipeline Step 2  → src/data/api_specs/ (create or update)
/bot-develop Step 2    → src/data/api_specs/ (create or update)
```

## Staleness Detection

The orchestrator should periodically check (on `/checkpointing` or session start):

1. **CLAUDE.md Zone C**: >50 lines? → Summarize older entries
2. **DESIGN.md**: Last updated >30 days ago while code changed significantly? → Flag for review
3. **api_specs/**: Any spec >6 months old? → Flag for re-research
4. **CODEX_HANDOFF_PLAYBOOK.md**: New skills added since last update? → Flag for new templates
