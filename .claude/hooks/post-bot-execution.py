#!/usr/bin/env python3
"""PostToolUse hook (Bash): Detect bot execution errors, connection failures,
and trading errors in bot-related commands.
"""

import json
import re
import sys

BOT_COMMANDS = [
    "python src/bot", "python -m src.bot", "docker compose",
    "docker run", "systemctl", "uvicorn", "gunicorn",
]

BOT_ERROR_PATTERNS = [
    (r"ConnectionError|ConnectionRefused|ConnectionReset", "Connection failure"),
    (r"TimeoutError|ReadTimeout|ConnectTimeout", "Timeout"),
    (r"AuthenticationError|InvalidApiKey|InvalidSignature", "API authentication error"),
    (r"InsufficientBalance|InsufficientFunds", "Insufficient balance"),
    (r"OrderNotFound|InvalidOrder|OrderRejected", "Order error"),
    (r"RateLimitExceeded|DDoSProtection|ExchangeNotAvailable", "Rate limit / exchange unavailable"),
    (r"NetworkError|RequestTimeout", "Network error"),
    (r"ExchangeError|BadRequest|BadResponse", "Exchange API error"),
    (r"WebSocket.*(?:closed|error|failed|disconnect)", "WebSocket disconnection"),
    (r"position.*(?:stuck|orphan|inconsistent)", "Position inconsistency"),
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

    # Only check bot-related commands
    if not any(bc in command for bc in BOT_COMMANDS):
        sys.exit(0)

    tool_output = data.get("tool_output", {})
    stdout = tool_output.get("stdout", "")
    stderr = tool_output.get("stderr", "")
    output = f"{stdout}\n{stderr}"

    if len(output.strip()) < 10:
        sys.exit(0)

    detected: list[str] = []
    for pattern, label in BOT_ERROR_PATTERNS:
        if re.search(pattern, output, re.IGNORECASE):
            detected.append(label)

    if not detected:
        sys.exit(0)

    error_types = ", ".join(set(detected))
    snippet = output[:500].strip()

    # Determine severity
    critical_types = {"Insufficient balance", "Position inconsistency", "API authentication error"}
    is_critical = bool(set(detected) & critical_types)

    severity = "CRITICAL" if is_critical else "WARNING"
    action = (
        "IMMEDIATE: Consider running `/incident-response` to handle this incident.\n"
        "Check exchange status and bot logs."
        if is_critical
        else "Monitor the situation. If persistent, use `/incident-response`."
    )

    context = (
        f"BOT {severity} ({error_types}):\n"
        f"Command: `{command}`\n"
        f"```\n{snippet}\n```\n"
        f"{action}"
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
