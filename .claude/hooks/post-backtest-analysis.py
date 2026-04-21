#!/usr/bin/env python3
"""PostToolUse hook (Bash): Detect backtest execution commands and suggest
automatic result analysis and performance threshold checks.
"""

import json
import re
import sys

BACKTEST_KEYWORDS = [
    "backtest", "backtrader", "vectorbt", "run_backtest",
    "cerebro.run", "vbt.Portfolio", "bt.run",
]

METRIC_PATTERNS = {
    "sharpe": (r"[Ss]harpe.*?(-?[\d.]+)", 1.0, "Sharpe Ratio below 1.0"),
    "max_dd": (r"[Mm]ax.*?[Dd]rawdown.*?(-?[\d.]+)%?", 20.0, "Max Drawdown exceeds 20%"),
    "win_rate": (r"[Ww]in.*?[Rr]ate.*?([\d.]+)%?", 40.0, "Win Rate below 40%"),
    "profit_factor": (r"[Pp]rofit.*?[Ff]actor.*?([\d.]+)", 1.5, "Profit Factor below 1.5"),
}


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

    # Check if this is a backtest command
    command_lower = command.lower()
    if not any(kw in command_lower for kw in BACKTEST_KEYWORDS):
        sys.exit(0)

    tool_output = data.get("tool_output", {})
    stdout = tool_output.get("stdout", "")

    warnings: list[str] = []

    # Check performance thresholds
    for metric_name, (pattern, threshold, warning_msg) in METRIC_PATTERNS.items():
        match = re.search(pattern, stdout)
        if match:
            try:
                value = float(match.group(1))
                if metric_name == "sharpe" and value < threshold:
                    warnings.append(f"WARNING: {warning_msg} (actual: {value:.4f})")
                elif metric_name == "max_dd" and abs(value) > threshold:
                    warnings.append(f"WARNING: {warning_msg} (actual: {abs(value):.2f}%)")
                elif metric_name == "win_rate" and value < threshold:
                    warnings.append(f"WARNING: {warning_msg} (actual: {value:.2f}%)")
                elif metric_name == "profit_factor" and value < threshold:
                    warnings.append(f"WARNING: {warning_msg} (actual: {value:.4f})")
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
