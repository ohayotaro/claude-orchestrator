#!/usr/bin/env python3
"""PostToolUse hook (Bash): Detect error patterns in command output and suggest
routing to the codex-debugger subagent.
"""

import json
import re
import sys

# Commands to ignore (trivial, unlikely to need debugging)
IGNORE_COMMANDS = [
    "git ", "ls ", "cd ", "pwd", "echo ", "cat ", "head ", "tail ",
    "which ", "mkdir ", "touch ", "cp ", "mv ",
]

# Error patterns to detect
ERROR_PATTERNS = [
    (r"Traceback \(most recent call last\)", "Python traceback"),
    (r"FAILED|ERRORS?|failures?", "Test failure"),
    (r"ModuleNotFoundError|ImportError", "Import error"),
    (r"TypeError|ValueError|KeyError|AttributeError", "Python runtime error"),
    (r"SyntaxError", "Syntax error"),
    (r"error\[E\d+\]", "MQL5 compilation error"),
    (r"ConnectionError|TimeoutError|HTTPError", "Network/API error"),
    (r"PermissionError|FileNotFoundError|OSError", "System error"),
    (r"panic:|SIGABRT|SIGSEGV|core dumped", "Crash"),
    (r"npm ERR!|yarn error", "Node.js package error"),
]


def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        sys.exit(0)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "")

    # Skip trivial commands
    if any(command.startswith(prefix) for prefix in IGNORE_COMMANDS):
        sys.exit(0)

    tool_output = data.get("tool_output", {})
    stdout = tool_output.get("stdout", "")
    stderr = tool_output.get("stderr", "")
    output = f"{stdout}\n{stderr}"

    if len(output.strip()) < 10:
        sys.exit(0)

    detected: list[str] = []
    for pattern, label in ERROR_PATTERNS:
        if re.search(pattern, output, re.IGNORECASE):
            detected.append(label)

    if not detected:
        sys.exit(0)

    # Truncate output for context (first 500 chars)
    error_snippet = output[:500].strip()
    error_types = ", ".join(set(detected))

    context = (
        f"ERROR DETECTED ({error_types}):\n"
        f"Command: `{command}`\n"
        f"```\n{error_snippet}\n```\n"
        "Consider delegating to the codex-debugger subagent for root cause analysis:\n"
        "Use agent type 'codex-debugger' or run:\n"
        f'`codex --full-auto "Debug: {error_types} in command: {command}"`'
    )

    result = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": context,
        }
    }
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
