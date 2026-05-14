---
name: strategy-register
description: Manage the strategy registry — register new strategies, transition lifecycle states, allocate MagicNumber, list and audit. Single source of truth for strategy identity per .claude/rules/multi-strategy.md.
agent: strategist
allowed-tools: "Bash(uv *) Bash(python *) Bash(git *) Read Write Edit Glob Grep"
---

# Strategy Registry

This skill is the **only** sanctioned writer of `config/registry.toml`. All other skills MUST go through it (or read-only operations) to touch strategy identity.

Contract: `.claude/rules/multi-strategy.md`. If that document and this skill disagree, the rule wins — fix this skill.

## Subcommands

Invoke with the action as the first argument:

| Action | Purpose |
|---|---|
| `register` | Mint a new `strategy_id`, allocate MagicNumber (mql5), scaffold per-strategy directories and config skeleton |
| `transition` | Move a strategy through its lifecycle (`draft → testnet → live → deprecated → retired`) |
| `enable` / `disable` | Flip the runtime `enabled` flag without changing state |
| `list` | Print the registry, optionally filtered by state / risk_group / venue |
| `show` | Print one strategy's full registry entry plus path existence checks |
| `audit` | Verify registry invariants (regex, magic uniqueness, path existence, state transitions valid) |

If the user invokes `/strategy-register` without an action, ask which one they want and show the table above.

## Workflow: `register`

### Step 1: Gather inputs
Ask the user (or accept from a calling skill):
1. `venue` (e.g., `binance`, `oanda`, `ibkr`)
2. `market` (e.g., `spot`, `swap`, `fx`, `cash`)
3. `logic_slug` (e.g., `mean-revert`, `ma-cross`) — must be lowercase, kebab-case
4. `symbol` (exchange-native form, e.g., `BTCUSDT`)
5. `timeframe` (e.g., `5m`, `1h`)
6. `runtime` (`python` or `mql5`)
7. `account_scope` (project-defined label)
8. `risk_group` (project-defined label)
9. `family_id` (defaults to `logic_slug` unless multiple variants share lineage)
10. `logic_version` (semver, default `0.1.0` for a fresh draft)

### Step 2: Canonicalize and compose `strategy_id`
- Lowercase the symbol and strip separators: `BTC/USDT` → `btcusdt`, `7203.T` → `7203t`.
- Compose: `{venue}.{market}.{logic_slug}.{symbol_canonical}.{timeframe}.v{major}` where `major` is parsed from `logic_version`'s major component (start at `v1`).
- Validate against the canonical regex in `multi-strategy.md` §2.
- Reject if the regex fails. Suggest the closest legal form.

### Step 3: Check uniqueness
- Refuse if `strategy_id` already exists in `config/registry.toml`.
- Refuse if a near-duplicate exists (same venue / market / logic / symbol / timeframe but different formatting) — this is the canonicalization safeguard.

### Step 4: Allocate MagicNumber (mql5 only)
Implement the algorithm from `multi-strategy.md` §3 exactly:
```python
import zlib
RANGE_START = 20_000_000
RANGE_SIZE = 70_000_000

MAX_SALT_ITERATIONS = 1000

def allocate_magic(strategy_id: str, existing: set[int]) -> tuple[int, int]:
    for salt in range(MAX_SALT_ITERATIONS):
        key = strategy_id if salt == 0 else f"{strategy_id}#{salt}"
        candidate = RANGE_START + (zlib.crc32(key.encode()) % RANGE_SIZE)
        if candidate not in existing:
            return candidate, salt
    raise RuntimeError(
        f"MagicNumber allocation exhausted after {MAX_SALT_ITERATIONS} iterations "
        f"for strategy_id={strategy_id}. Registry has {len(existing)} entries."
    )
```

Freeze both `magic_number` and `magic_salt` in the registry entry.

For `runtime = "python"`, set `magic_number = 0` and `magic_salt = 0` (unused).

### Step 5: Compose paths
Using `[defaults]` from the registry header:
- `config_path = "{config_dir}/{strategy_id}.toml"`
- `state_path  = "{state_dir}/{strategy_id}"`
- `log_path   = "{log_dir}/{strategy_id}"`
- `db_path    = "{state_path}/state.db"` (python only)

### Step 6: Write registry entry
Append a `[[strategies]]` block with:
- All required fields per `multi-strategy.md` §4
- `state = "draft"`
- `enabled = false`
- `created_at` and `updated_at` set to current RFC3339 UTC timestamp
- `owner` set from `git config user.email` if available, else empty

Format: insert in alphabetical `id` order to minimize merge conflicts.

### Step 7: Scaffold per-strategy artifacts
Create:
- `{config_path}` from the per-strategy TOML template (see §"Templates" below)
- `{state_path}/` (empty directory; `.gitkeep` to track)
- `{log_path}/` (empty directory; `.gitkeep` to track)
- `reports/strategies/{strategy_id}/` (empty directory; `.gitkeep`)

Do NOT scaffold runtime code (bot or EA) — that belongs to `/bot-develop` or `/ea-generate`.

### Step 8: Report
Print:
```
Registered: {strategy_id}
  family:        {family_id}
  runtime:       {runtime}
  magic_number:  {magic_number}   (mql5 only)
  config_path:   {config_path}
  state:         draft
  enabled:       false

Next steps:
  - Edit {config_path} to set parameters and risk limits
  - For Python: /bot-develop {strategy_id}
  - For MQL5:   /ea-generate  {strategy_id}
  - After testnet validation: /strategy-register transition {strategy_id} testnet
```

## Workflow: `transition`

### Step 1: Validate transition
Accept `transition {strategy_id} {target_state}`.

Allowed transitions (must match `multi-strategy.md` §4):
```
draft     → testnet | deprecated
testnet   → live | deprecated
live      → deprecated
deprecated→ retired
```

Reject everything else with a clear error.

### Step 2: Enforce preconditions
Per target state:

**→ testnet**
- Per-strategy config file exists and parses
- Runtime artifact exists (`/bot-develop` ran for python, `/ea-generate` ran for mql5)
- Backtest report exists in `reports/strategies/{strategy_id}/`

**→ live**
- Must currently be `testnet`.
- ALL of `multi-strategy.md` §4 "Preconditions for `live` promotion":
  1. Testnet evidence within last 7 days
  2. `MAX_POSITION_SIZE` and `MAX_DAILY_LOSS` set in per-strategy config
  3. Stop loss implementation verified
  4. KillSwitch end-to-end test passed
  5. Notification webhook smoke test passed
  6. `/risk-report` generated within last 7 days for this `strategy_id`
- If any precondition is missing, print the checklist with [x] / [ ] markers and refuse the transition.
- Note: this skill does NOT itself flip the live-trading acknowledgment file (`.claude/state/live-trading-*.ack`). That is a separate, daily, human-acknowledged gate handled by `security.md` / `bot-deploy`.

**→ deprecated**
- Always allowed (from `draft`, `testnet`, or `live`).
- If transitioning from `live`, force `enabled = false`.

**→ retired**
- Must currently be `deprecated`.
- Verify no recent activity in `state_path` (no log entries / state changes in last 30 days).
- Note: retiring does NOT delete files. Files remain for audit. Use a separate operator action to archive.

### Step 3: Update entry
- Set `state = {target_state}`.
- Set `updated_at` to current RFC3339 UTC timestamp.
- For `→ live`, do NOT auto-flip `enabled`. The operator must explicitly `/strategy-register enable {strategy_id}` after deployment is healthy.

### Step 4: Report and recommend
For `→ live`, output the live-trading checklist from `security.md` and remind the operator to create today's acknowledgment.

## Workflow: `enable` / `disable`

- `enable {strategy_id}`: refuse if `state != "live"`. Otherwise set `enabled = true`.
- `disable {strategy_id}`: allowed in any state. Set `enabled = false`.
- Update `updated_at`.
- Do NOT close existing positions — that is `/incident-response` or `/bot-deploy` territory.

## Workflow: `list`

Print a table:
```
strategy_id                                          runtime  state       enabled  risk_group
binance.swap.mean-revert.btcusdt.5m.v1               python   live        true     crypto-main
oanda.fx.ma-cross.usdjpy.1h.v1                       mql5     testnet     false    fx-main
```

Accept filters as flags: `--state live`, `--risk-group crypto-main`, `--venue binance`, `--runtime mql5`.

## Workflow: `show`

Print the full registry entry as TOML, then a sanity section:
```
Paths (exists?):
  config_path:   config/strategies/{id}.toml          [ok]
  state_path:    state/strategies/{id}/               [ok]
  log_path:      logs/strategies/{id}/                [ok]
  db_path:       state/strategies/{id}/state.db       [missing — not yet created]
```

## Workflow: `audit`

Verify registry invariants. Report violations with severity:

1. **strategy_id format** — every `id` matches the canonical regex.
2. **uniqueness** — no two entries share the same `id`.
3. **MagicNumber uniqueness** — among `runtime = "mql5"` entries, all `magic_number` values are distinct AND within the reserved range.
4. **state validity** — `state` is one of the five allowed values.
5. **path declaration** — `config_path`, `state_path`, `log_path` follow the defaults pattern.
6. **path existence** — declared paths exist (or scaffold `.gitkeep` if missing — prompt user).
7. **timestamp sanity** — `updated_at >= created_at`; RFC3339 parseable.
8. **canonicalization** — no near-duplicate symbols (e.g., `btcusdt` and `btc-usdt` in different entries).
9. **runtime field coherence** — `magic_number > 0` iff `runtime = "mql5"`.

Exit code 0 if clean, non-zero otherwise. This skill's audit is intended to be runnable from CI.

## Templates

### Per-strategy config TOML (created at register-time)
```toml
# {strategy_id}
strategy_id = "{strategy_id}"

[runtime]
mode = "testnet"            # testnet | live | dry-run
symbol = "{symbol}"
timeframe = "{timeframe}"

[risk]
max_position_size = 0.01        # in base currency / lots — adjust per market
max_daily_loss_pct = 2.0
max_drawdown_pct = 10.0
stop_loss_pct = 1.0
take_profit_pct = 2.0

[params]
# Strategy-specific parameters -- filled by /strategy-design or operator

[notifications]
# Optional. Per-strategy alert routing. If absent, alerts fall back to the
# project-default channel. Risk-group aggregate alerts use risk_groups.toml,
# not this section.
# channel = "slack://#bot-alerts"
# severity_floor = "WARNING"   # only forward events >= this level
```

### Atomic write requirement
- Always write `config/registry.toml` to a temp file in the same directory, then `os.replace()` over the original. The registry MUST NOT be left half-written if the process is killed.
- The advisory file lock (`fcntl.flock` on POSIX) MUST be held for the entire read-modify-write cycle, NOT just the write. Concretely, for `register` this means: acquire the lock BEFORE Step 3 (uniqueness check), hold it through Step 4 (MagicNumber allocation -- the read of existing magic numbers is part of the protected region) and Step 6 (write). Releasing the lock between read and write would let two concurrent registrations both observe the same "existing" set and collide.
- The MagicNumber salt-collision loop MUST be bounded (e.g., max 1000 iterations). On exhaustion, error out cleanly -- never spin forever.

## Implementation Notes

- Implementation language: Python, using `tomllib` (read) and `tomli_w` (write). Add `tomli_w` to project deps if missing.
- Reference implementation lives at `src/orchestrator/registry.py` (created on first `register` if missing). The skill MAY shell out to `uv run python -m orchestrator.registry {action} {args}` to keep the registry logic testable.
- Unit tests live under `tests/test_orchestrator/test_registry.py` and MUST cover: regex validation, MagicNumber collision path, lifecycle transitions, audit invariants.

## Codex Delegation

For complex registry decisions (e.g., schema migration when bumping `schema_version`), delegate to Codex per `.claude/docs/CODEX_HANDOFF_PLAYBOOK.md`. There is currently no dedicated playbook section for registry consultation — add one if you find yourself reaching for Codex repeatedly here.

## Failure Handling

If any step fails (registry parse error, path collision, magic allocation exhaustion):
1. Roll back any partial writes -- the registry file MUST remain valid TOML at all times.
2. Print the exact failure with the relevant section of `multi-strategy.md` cited.
3. Do NOT proceed to scaffold artifacts on the filesystem if the registry write failed.

### Crash between registry write and scaffolding
If Step 6 (registry write) succeeded but Step 7 (per-strategy directory scaffolding) failed or was interrupted, the registry now references paths that may not exist. Recovery options, in order of preference:

1. **Idempotent re-run**: Step 7 uses `mkdir -p` and `.gitkeep` writes that are safe to re-run. The operator can re-invoke `/strategy-register register` with the same arguments; it will detect the existing registry entry and offer to "complete scaffolding" rather than re-register.
2. **Audit auto-fix**: `audit --fix` MUST detect missing directories declared in the registry and re-create them. Without `--fix`, audit reports them as a violation.
3. **Manual deregister**: if the entry is unsalvageable, the operator invokes `/strategy-register transition {id} deprecated` followed by manual removal once retention is over. The registry entry itself is never silently deleted.

The registry write is therefore the commit point. Anything after it is recoverable; anything before it leaves the registry untouched.

## Anti-Patterns

- Editing `registry.toml` by hand. Always go through this skill.
- Re-deriving MagicNumber from `strategy_id` at runtime. Read the frozen value from the registry.
- Skipping audit before opening a PR that touches multiple registry entries.
- Using `register` to "rename" a strategy. There is no rename — register a new `v<major+1>` and deprecate the old one.
