#!/usr/bin/env python3
"""PostToolUse hook (Edit|Write): Run linting after file modifications.
- .py files: ruff check
- .mq5 files: basic syntax check (placeholder)
"""

import json
import os
import subprocess
import sys


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

    _, ext = os.path.splitext(file_path)

    if ext == ".py":
        try:
            result = subprocess.run(
                ["ruff", "check", file_path, "--select", "E,F,I"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0 and result.stdout.strip():
                lint_output = result.stdout.strip()[:500]
                hook_result = {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": (
                            f"LINT: ruff found issues in {os.path.basename(file_path)}:\n"
                            f"```\n{lint_output}\n```\n"
                            "Consider fixing these before proceeding."
                        ),
                    }
                }
                json.dump(hook_result, sys.stdout)
                return
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # ruff not installed or timed out — skip silently
            pass

    elif ext in (".mq5", ".mq4", ".mqh"):
        # MQL5 basic check — just verify file is not empty and has #property
        if os.path.exists(file_path):
            try:
                with open(file_path) as f:
                    content = f.read(1000)
                if "#property" not in content and len(content) > 100:
                    hook_result = {
                        "hookSpecificOutput": {
                            "hookEventName": "PostToolUse",
                            "additionalContext": (
                                f"MQL5 CHECK: {os.path.basename(file_path)} "
                                "is missing `#property strict` directive."
                            ),
                        }
                    }
                    json.dump(hook_result, sys.stdout)
                    return
            except OSError:
                pass

    sys.exit(0)


if __name__ == "__main__":
    main()
