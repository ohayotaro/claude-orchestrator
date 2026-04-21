#!/usr/bin/env python3
"""PreToolUse hook (WebSearch|WebFetch): Detect comprehensive research queries
and suggest delegating to Gemini or an Opus subagent to conserve context.
"""

import json
import sys

RESEARCH_KEYWORDS = [
    "documentation", "best practice", "comparison", "benchmark",
    "tutorial", "guide", "reference", "specification",
    "academic", "paper", "research", "study",
    "alternative", "library", "framework",
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
    query = tool_input.get("query", "") or tool_input.get("url", "")
    if not query:
        sys.exit(0)

    query_lower = query.lower()
    matched = [kw for kw in RESEARCH_KEYWORDS if kw in query_lower]

    if len(matched) < 2:
        sys.exit(0)

    context = (
        "RESEARCH SUGGESTION: This appears to be a comprehensive research query "
        f"(matched: {', '.join(matched)}).\n"
        "To conserve context, consider:\n"
        "1. Delegating to Gemini CLI: `gemini -p \"{query}\"`\n"
        "2. Using an Opus subagent for deep research\n"
        "Large research results can quickly consume the context window."
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
