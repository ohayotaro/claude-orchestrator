#!/usr/bin/env python3
"""PreToolUse hook (Edit|Write): Check if the file being modified involves
design/architecture decisions that should be reviewed by Codex first.
"""

import json
import os
import sys

# Paths that typically contain design decisions
DESIGN_PATHS = [
    "src/strategies/",
    "src/risk/",
    "src/optimization/",
    "mql5/experts/",
    "mql5/include/",
]

# File patterns indicating config/architecture
CONFIG_PATTERNS = [
    "pyproject.toml",
    "config",
    "__init__.py",
]

# Code patterns indicating design decisions
DESIGN_PATTERNS = [
    "class ",
    "class(",
    "def __init__",
    "ABC",
    "abstractmethod",
    "Protocol",
    "@dataclass",
]

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB safety limit


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

    # Security: prevent path traversal
    real_path = os.path.realpath(file_path)
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if project_dir and not real_path.startswith(os.path.realpath(project_dir)):
        print("Path traversal detected", file=sys.stderr)
        sys.exit(2)

    reasons: list[str] = []

    # Check if file is in a design-critical path
    for design_path in DESIGN_PATHS:
        if design_path in file_path:
            reasons.append(f"File is in design-critical path: {design_path}")
            break

    # Check if file is a config file
    basename = os.path.basename(file_path)
    for pattern in CONFIG_PATTERNS:
        if pattern in basename:
            reasons.append(f"File appears to be a configuration file: {basename}")
            break

    # Check content for design patterns (for Edit tool with old_string)
    content = tool_input.get("new_string", "") or tool_input.get("content", "")
    for pattern in DESIGN_PATTERNS:
        if pattern in content:
            reasons.append(f"Content contains design pattern: '{pattern}'")
            break

    if not reasons:
        sys.exit(0)

    context = (
        "DESIGN CHECK: This edit involves design/architecture decisions.\n"
        f"Reasons: {'; '.join(reasons)}\n"
        "Consider consulting Codex CLI before proceeding:\n"
        "`codex exec \"Review this design change: {context}\"`"
    )

    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": context,
        }
    }
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
