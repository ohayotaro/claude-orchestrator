#!/usr/bin/env python3
"""UserPromptSubmit hook: Analyze user prompt and suggest optimal AI routing.

Priority:
  1. Gemini — multimodal file references (images, PDFs)
  2. Codex  — design, debug, optimization, algorithm keywords
  3. Specialized subagent — financial domain keywords
"""

import json
import re
import sys


def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        sys.exit(0)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit(0)

    prompt = data.get("prompt", "")
    if len(prompt) < 10:
        sys.exit(0)

    prompt_lower = prompt.lower()
    suggestions: list[str] = []

    # --- Priority 1: Gemini (multimodal) ---
    multimodal_patterns = [
        r"\.(png|jpg|jpeg|gif|svg|webp|bmp|tiff)",
        r"\.(pdf|doc|docx|xls|xlsx)",
        r"chart|チャート|画像|image|screenshot|スクリーンショット",
    ]
    for pattern in multimodal_patterns:
        if re.search(pattern, prompt_lower):
            suggestions.append(
                "ROUTING: This task involves multimodal input. "
                "Consider delegating to Gemini CLI: "
                '`gemini -p "{prompt}" -f {file}`'
            )
            break

    # --- Priority 2: Codex (deep reasoning) ---
    codex_keywords = [
        "design", "architect", "debug", "error", "traceback",
        "optimize", "algorithm", "review", "refactor",
        "設計", "デバッグ", "エラー", "最適化", "レビュー",
    ]
    if any(kw in prompt_lower for kw in codex_keywords):
        suggestions.append(
            "ROUTING: This task may benefit from deep reasoning. "
            "Consider delegating to Codex CLI: "
            "`codex --approval-mode suggest \"{task}\"`"
        )

    # --- Priority 3: Specialized subagent ---
    agent_routing = {
        "data-engineer": [
            "data", "fetch", "pipeline", "ohlcv", "parquet",
            "binance", "bybit", "yfinance", "mt5",
            "データ", "取得", "パイプライン",
        ],
        "quant-analyst": [
            "backtest", "sharpe", "sortino", "drawdown", "var",
            "cvar", "monte carlo", "walk-forward", "bootstrap",
            "バックテスト", "リスク",
        ],
        "strategist": [
            "strategy", "signal", "entry", "exit", "indicator",
            "rsi", "macd", "moving average", "crossover",
            "ストラテジー", "シグナル", "戦略",
        ],
        "ea-developer": [
            "ea", "expert advisor", "mql5", "mql4", "metatrader",
            "ontick", "ctrade",
        ],
        "bot-engineer": [
            "bot", "ccxt", "websocket", "async", "executor",
            "live trading", "order manager", "position tracker",
            "python-binance", "pybit", "testnet", "sandbox",
            "ボット", "自動売買", "ライブ",
        ],
        "infra-ops": [
            "deploy", "docker", "dockerfile", "compose",
            "systemd", "kubernetes", "k8s", "vps", "cloud",
            "monitor", "alert", "grafana", "prometheus",
            "health check", "log", "ci/cd", "pipeline",
            "dashboard", "fastapi", "notification", "discord",
            "launchd", "plist",
            "デプロイ", "監視", "インフラ", "ダッシュボード", "通知",
        ],
        "ml-engineer": [
            "machine learning", "ml", "model", "train", "feature",
            "hmm", "lightgbm", "xgboost", "cnn", "lstm",
            "clustering", "kmeans", "gmm", "hdbscan", "som",
            "regime", "classification", "walk-forward", "purge",
            "optuna", "hyperparameter", "ablation", "overfitting",
            "機械学習", "特徴量", "レジーム", "学習",
        ],
    }

    for agent, keywords in agent_routing.items():
        if any(kw in prompt_lower for kw in keywords):
            suggestions.append(
                f"ROUTING: Consider using the '{agent}' subagent for this task."
            )

    if not suggestions:
        sys.exit(0)

    result = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": "\n".join(suggestions),
        }
    }
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
