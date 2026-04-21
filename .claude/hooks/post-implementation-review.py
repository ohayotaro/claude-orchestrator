#!/usr/bin/env python3
"""PostToolUse hook (Edit|Write): Track changes per session. When thresholds
are exceeded (3+ files or 100+ lines), suggest a Codex code review.
"""

import json
import os
import sys
import time

STATE_FILE = os.path.join(
    os.environ.get("CLAUDE_PROJECT_DIR", "."),
    ".claude", "logs", "session-changes.json",
)

FILES_THRESHOLD = 3
LINES_THRESHOLD = 100


def load_state() -> dict:
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
        # Reset if older than 2 hours (likely new session)
        if time.time() - state.get("started_at", 0) > 7200:
            return {"started_at": time.time(), "files": [], "total_lines": 0, "suggested": False}
        return state
    except (FileNotFoundError, json.JSONDecodeError):
        return {"started_at": time.time(), "files": [], "total_lines": 0, "suggested": False}


def save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def count_meaningful_lines(content: str) -> int:
    """Count non-empty, non-comment lines."""
    count = 0
    for line in content.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("//"):
            count += 1
    return count


def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        sys.exit(0)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    # Count new lines added
    content = tool_input.get("new_string", "") or tool_input.get("content", "")
    new_lines = count_meaningful_lines(content)

    state = load_state()

    if file_path not in state["files"]:
        state["files"].append(file_path)
    state["total_lines"] += new_lines

    save_state(state)

    # Check thresholds
    file_count = len(state["files"])
    total_lines = state["total_lines"]

    if state.get("suggested"):
        sys.exit(0)

    if file_count >= FILES_THRESHOLD or total_lines >= LINES_THRESHOLD:
        state["suggested"] = True
        save_state(state)

        context = (
            f"REVIEW SUGGESTION: Significant changes detected in this session.\n"
            f"Files modified: {file_count}, Lines added: {total_lines}\n"
            f"Consider running a code review via Codex:\n"
            "`codex --approval-mode suggest \"Review recent changes for quality and correctness\"`\n"
            "Or use `/team-review` for a comprehensive parallel review."
        )

        result = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": context,
            }
        }
        json.dump(result, sys.stdout)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
