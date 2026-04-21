#!/usr/bin/env python3
"""PostToolUse hook (Bash): Detect backtest execution commands and suggest
automatic result analysis and performance threshold checks.

Thresholds are loaded from .claude/backtest-thresholds.json if present,
otherwise built-in defaults are used.
"""

import json
import os
import re
import sys

BACKTEST_KEYWORDS = [
    "backtest", "backtrader", "vectorbt", "run_backtest",
    "cerebro.run", "vbt.Portfolio", "bt.run",
]

# Built-in defaults
DEFAULT_THRESHOLDS = {
    "sharpe": {
        "pattern": r"[Ss]harpe.*?(-?[\d.]+)",
        "threshold": 1.0,
        "comparison": "below",
        "message": "Sharpe Ratio below threshold",
    },
    "max_drawdown": {
        "pattern": r"[Mm]ax.*?[Dd]rawdown.*?(-?[\d.]+)%?",
        "threshold": 20.0,
        "comparison": "above",
        "message": "Max Drawdown exceeds threshold",
    },
    "win_rate": {
        "pattern": r"[Ww]in.*?[Rr]ate.*?([\d.]+)%?",
        "threshold": 40.0,
        "comparison": "below",
        "message": "Win Rate below threshold",
    },
    "profit_factor": {
        "pattern": r"[Pp]rofit.*?[Ff]actor.*?([\d.]+)",
        "threshold": 1.5,
        "comparison": "below",
        "message": "Profit Factor below threshold",
    },
}


def load_thresholds() -> dict:
    """Load thresholds from project config, fall back to defaults."""
    config_path = os.path.join(
        os.environ.get("CLAUDE_PROJECT_DIR", "."),
        ".claude", "backtest-thresholds.json",
    )
    try:
        with open(config_path) as f:
            config = json.load(f)
        thresholds = {k: v for k, v in config.items() if not k.startswith("_") and v}
        return thresholds if thresholds else DEFAULT_THRESHOLDS
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_THRESHOLDS


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

    command_lower = command.lower()
    if not any(kw in command_lower for kw in BACKTEST_KEYWORDS):
        sys.exit(0)

    tool_output = data.get("tool_output", {})
    stdout = tool_output.get("stdout", "")

    thresholds = load_thresholds()
    warnings: list[str] = []

    for metric_name, config in thresholds.items():
        pattern = config.get("pattern", "")
        threshold = config.get("threshold", 0)
        comparison = config.get("comparison", "below")
        message = config.get("message", f"{metric_name} threshold breached")

        match = re.search(pattern, stdout)
        if match:
            try:
                value = float(match.group(1))
                breached = False
                if comparison == "below" and value < threshold:
                    breached = True
                elif comparison == "above" and abs(value) > threshold:
                    breached = True

                if breached:
                    warnings.append(f"WARNING: {message} (actual: {value:.4f}, threshold: {threshold})")
            except (ValueError, IndexError):
                pass

    suggestions = [
        "BACKTEST COMPLETED. Recommended next steps:",
        "1. Review performance metrics against risk-management.md thresholds",
        "2. Run statistical validation via Codex: "
        '`codex --approval-mode suggest "Validate backtest results: {metrics}"`',
        "3. Check for look-ahead bias in strategy code",
        "4. Run Out-of-Sample test if not done",
    ]

    if warnings:
        suggestions.insert(0, "\n".join(warnings))

    context = "\n".join(suggestions)

    result = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": context,
        }
    }
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
