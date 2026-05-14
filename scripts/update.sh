#!/usr/bin/env bash
#
# update.sh — refresh the Financial Trading AI Orchestrator template in an
# existing project. Backs up Zone B + customizable JSON, pulls latest,
# restores backups.
#
# Usage (from project root):
#   bash <(curl -fsSL https://raw.githubusercontent.com/ohayotaro/claude-finance/main/scripts/update.sh)
#
# Or, if scripts/update.sh has already been copied locally:
#   ./scripts/update.sh
#
# Behavior:
#   1. Backs up CLAUDE.md Zone B (between @orchestra:template-boundary
#      and @orchestra:repo-boundary)
#   2. Backs up customizable JSON: routing-keywords.json,
#      backtest-thresholds.json
#   3. Clones the latest template into .starter-update/
#   4. Replaces ONLY template-managed paths (see lists below)
#   5. Restores Zone B and custom JSON from the backup
#   6. Cleans up
#
# What is preserved (NEVER touched by this script):
#   - .claude/projects/        — project memory (auto-memory)
#   - .claude/checkpoints/     — /checkpointing session state
#   - .claude/plans/           — Plan-mode output and user notes
#   - .claude/logs/            — agent team logs
#   - .claude/tmp/             — transient review artifacts
#   - .claude/docs/DESIGN.md   — project-specific ADRs
#   - .claude/docs/incidents/  — incident postmortems (permanent record)
#   - .claude/docs/reviews/    — past review artifacts
#   - .claude/settings.local.json — per-machine overrides
#   - any other file/dir under .claude/ not listed in TEMPLATE_PATHS below
#   - CLAUDE.md Zone B (backed up and restored)
#   - .claude/routing-keywords.json    (backed up and restored)
#   - .claude/backtest-thresholds.json (backed up and restored)
#
# What is overwritten:
#   - CLAUDE.md Zone A (template orchestration policy)
#   - .claude/agents/, .claude/hooks/, .claude/rules/, .claude/skills/
#   - .claude/docs/CODEX_HANDOFF_PLAYBOOK.md (file-level, not the docs/ dir)
#   - .claude/settings.json (re-add custom permissions afterward if needed;
#     prefer .claude/settings.local.json for per-machine overrides)
#   - .codex/, .gemini/
#
# Anything in your project tree (src/, mql5/, tests/, data/, reports/,
# pyproject.toml, etc.) is left untouched.

set -euo pipefail

REPO_URL="https://github.com/ohayotaro/claude-finance.git"
TMP_DIR=".starter-update"
BACKUP_ZONE_B=".zone-b.backup.md"
BACKUP_ROUTING=".routing-keywords.backup.json"
BACKUP_THRESHOLDS=".backtest-thresholds.backup.json"

red()    { printf "\033[31m%s\033[0m\n" "$*"; }
green()  { printf "\033[32m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }

require_file() {
  if [[ ! -f "$1" ]]; then
    red "Missing $1 — are you in the right project directory?"
    exit 1
  fi
}

# 1. Sanity check
if [[ ! -d ".claude" ]]; then
  red "No .claude/ here. Run this from the project root that already has the template installed."
  exit 1
fi
require_file "CLAUDE.md"

# 2. Backup Zone B
yellow "Backing up CLAUDE.md Zone B → $BACKUP_ZONE_B"
awk '
  /@orchestra:template-boundary/ { in_zone_b=1; next }
  /@orchestra:repo-boundary/     { in_zone_b=0; next }
  in_zone_b { print }
' CLAUDE.md > "$BACKUP_ZONE_B"

# 3. Backup customizable JSON
for pair in \
  ".claude/routing-keywords.json:$BACKUP_ROUTING" \
  ".claude/backtest-thresholds.json:$BACKUP_THRESHOLDS"; do
  src="${pair%%:*}"
  dst="${pair##*:}"
  if [[ -f "$src" ]]; then
    yellow "Backing up $src → $dst"
    cp "$src" "$dst"
  fi
done

# 4. Clone latest template
yellow "Cloning latest template into $TMP_DIR/"
rm -rf "$TMP_DIR"
git clone --depth 1 "$REPO_URL" "$TMP_DIR"

# 5. Overwrite ONLY template-managed paths inside .claude/.
#    User/project state (projects/, checkpoints/, plans/, logs/, tmp/,
#    settings.local.json, etc.) stays in place because we never delete
#    .claude/ as a whole.
# Template-managed directories: fully replaced.
# IMPORTANT: do NOT include `docs/` here. `.claude/docs/` mixes template files
# (CODEX_HANDOFF_PLAYBOOK.md) with project-specific permanent records (DESIGN.md,
# incidents/, reviews/). Use file-level replacement for docs instead.
TEMPLATE_DIRS_IN_CLAUDE=(agents hooks rules skills)

# Template-managed files: replaced individually. Paths are relative to .claude/.
TEMPLATE_FILES_IN_CLAUDE=(
  settings.json
  docs/CODEX_HANDOFF_PLAYBOOK.md
)

yellow "Replacing template-managed paths under .claude/"
for d in "${TEMPLATE_DIRS_IN_CLAUDE[@]}"; do
  rm -rf ".claude/$d"
  if [[ -d "$TMP_DIR/.claude/$d" ]]; then
    cp -R "$TMP_DIR/.claude/$d" ".claude/$d"
  fi
done
for f in "${TEMPLATE_FILES_IN_CLAUDE[@]}"; do
  if [[ -f "$TMP_DIR/.claude/$f" ]]; then
    mkdir -p "$(dirname ".claude/$f")"
    cp "$TMP_DIR/.claude/$f" ".claude/$f"
  fi
done

yellow "Replacing .codex/, .gemini/, CLAUDE.md"
rm -rf .codex .gemini
cp -R "$TMP_DIR/.codex" .codex
cp -R "$TMP_DIR/.gemini" .gemini
cp "$TMP_DIR/CLAUDE.md" CLAUDE.md

# 6. Restore Zone B
if [[ -s "$BACKUP_ZONE_B" ]]; then
  yellow "Restoring Zone B"
  python3 - "$BACKUP_ZONE_B" <<'PY'
import sys
from pathlib import Path

backup = Path(sys.argv[1]).read_text()
claude_md = Path("CLAUDE.md")
text = claude_md.read_text()

start = "@orchestra:template-boundary"
end = "@orchestra:repo-boundary"
i = text.find(start)
j = text.find(end)
if i == -1 or j == -1:
    print("[update.sh] CLAUDE.md missing boundary markers; skipping Zone B restore", file=sys.stderr)
    sys.exit(0)

# Replace content between the line containing `start` and the line containing `end`.
i_eol = text.find("\n", i)
new = text[:i_eol + 1] + "\n" + backup.rstrip("\n") + "\n\n" + text[j:]
claude_md.write_text(new)
PY
fi

# 7. Restore customizable JSON
for pair in \
  "$BACKUP_ROUTING:.claude/routing-keywords.json" \
  "$BACKUP_THRESHOLDS:.claude/backtest-thresholds.json"; do
  src="${pair%%:*}"
  dst="${pair##*:}"
  if [[ -f "$src" ]]; then
    yellow "Restoring $dst"
    mv "$src" "$dst"
  fi
done

# 8. Make hooks executable
chmod +x .claude/hooks/*.py 2>/dev/null || true

# 9. Cleanup
rm -rf "$TMP_DIR"
rm -f "$BACKUP_ZONE_B"

green "Update complete."
yellow "Next steps:"
echo "  - Review changes: git diff"
echo "  - Re-add custom permissions to .claude/settings.json if you had any"
echo "    (prefer .claude/settings.local.json for per-machine overrides)"
echo "  - Run /init-finance if Zone B fields need reconfiguration"
