# Financial Trading AI Orchestrator — Specification

Version 0.4.0 | Last updated: 2026-04-21

## 1. Overview

本システムは Claude Code (Opus 4.6, 1M context) をオーケストレーターとし、Codex CLI (GPT-5.4) および Gemini CLI (Gemini 2.5 Pro) を専門エージェントとして統合する、金融トレーディングAIチーム構成テンプレートである。

**対象市場**: 暗号資産、外国為替、先物、株式（取引所・通貨・戦略に非依存）

**設計原則**:
- オーケストレーターは委譲のみ行い、自ら実装しない
- 金融ドメインの正確性を最優先とする（ルックアヘッドバイアス禁止、取引コスト必須、OOS検証必須）
- すべてのエージェント指示は英語（LLM性能・トークン効率最適化）、ユーザー対話は日本語

## 2. System Architecture

```
┌─────────────────────────────────────────────────┐
│            Claude Code (Opus 4.6, 1M)           │
│            ── Orchestrator ──                    │
│  委譲判断 / コンテキスト管理 / 結果統合          │
├─────────────┬──────────────┬────────────────────┤
│  Subagents  │  Codex CLI   │    Gemini CLI       │
│  (Opus)     │  (GPT-5.4)   │    (Gemini 2.5 Pro) │
│             │              │                    │
│ コードベース │ 設計判断     │ マルチモーダル      │
│ 軽量レビュー │ 統計検証     │ チャート/PDF解析    │
│ テスト生成  │ デバッグ     │ リサーチ            │
└─────────────┴──────────────┴────────────────────┘
```

### 2.1 Delegation Triggers

| 条件 | 委譲先 |
|------|--------|
| 出力 10 行超 | Subagent or Codex |
| 2 ファイル以上の編集 | `/team-implement` (Agent Teams) |
| 3 ファイル以上の読み込み | Opus Subagent |
| 設計判断・アルゴリズム設計 | Codex CLI |
| 画像・PDF・マルチモーダル入力 | Gemini CLI |
| エラー分析 | `codex-debugger` Subagent |
| Bot 開発 (API/WebSocket) | `bot-engineer` Subagent |
| インフラ・デプロイ | `infra-ops` Subagent |

### 2.2 Hook-Driven Routing

9 つの Python Hook がツール呼び出しをインターセプトし、ルーティングを自動制御する:

| Hook | Event | 動作 |
|------|-------|------|
| `agent-router.py` | UserPromptSubmit | プロンプト解析 → 最適エージェント提案 |
| `check-codex-before-write.py` | PreToolUse (Edit/Write) | 設計判断を含むファイル編集時に Codex レビューを推奨 |
| `suggest-gemini-research.py` | PreToolUse (WebSearch/WebFetch) | 包括的リサーチクエリ検出 → Gemini 委譲提案 |
| `error-to-codex.py` | PostToolUse (Bash) | エラーパターン検出 → `codex-debugger` 提案 |
| `post-backtest-analysis.py` | PostToolUse (Bash) | バックテスト結果の閾値チェック（設定駆動） |
| `post-bot-execution.py` | PostToolUse (Bash) | Bot 実行エラー・接続断検出 |
| `post-implementation-review.py` | PostToolUse (Edit/Write) | 変更量閾値超過時に Codex レビュー提案 |
| `lint-on-save.py` | PostToolUse (Edit/Write) | Python: ruff / MQL5: 構文チェック |
| `log-cli-tools.py` | PostToolUse (Bash) | Codex/Gemini CLI 使用ログ記録 |

ルーティングキーワードは `.claude/routing-keywords.json` で外部設定可能。バックテスト閾値は `.claude/backtest-thresholds.json` で設定可能。いずれもフォールバックとしてビルトインデフォルト値を保持する。

## 3. Agent Definitions

9 専門エージェントが `.claude/agents/` に定義される。各エージェントは Protocol ベースの契約（専門領域、行動原則、応答フォーマット）を持つ。

| Agent | 専門領域 | 担当スコープ |
|-------|---------|-------------|
| `data-engineer` | データパイプライン、CEX/ブローカーAPI、コーポレートアクション | `src/data/*` |
| `quant-analyst` | バックテスト、統計検証、リスク計量、パフォーマンス評価 | `src/backtesting/*`, `src/risk/*` |
| `strategist` | シグナル設計、エントリー/エグジット、セクターローテーション、イベントドリブン | `src/strategies/*` |
| `ea-developer` | MQL5 EA 実装（OnInit/OnTick/OnDeinit、CTrade、マジックナンバー管理） | `mql5/*` |
| `bot-engineer` | API Bot (ccxt/WebSocket)、注文状態遷移、状態永続化、取引所固有アダプター | `src/bot/*` |
| `infra-ops` | Docker/systemd/launchd デプロイ、CI/CD、Prometheus/Grafana、通知 | `docker/*`, `src/monitoring/*` |
| `ml-engineer` | 教師あり/なし学習、特徴量エンジニアリング、walk-forward (purge/embargo)、過学習検出 | ML パイプライン |
| `codex-debugger` | エラー根本原因分析（Codex CLI 委譲） | 全ファイル |
| `general-purpose` | コードベース探索、ドキュメント生成、軽量レビュー | 全ファイル |

## 4. Skills（25 スキル）

### 4.1 Skill Pipeline

```
Strategy Dev:  /data-pipeline → /strategy-design → /backtest → /optimize ─┬→ /ea-generate
                                                                           └→ /bot-develop → /bot-deploy → /bot-monitor
ML Pipeline:   /data-pipeline → /ml-pipeline → /backtest → /optimize → /bot-develop
Equity:        /equity-screener → /earnings-calendar → /sector-analysis → /ir-analysis → /strategy-design
Operations:    /live-trading, /incident-response, /risk-report
```

### 4.2 Skill Catalog

| # | Skill | 分類 | 概要 | 主要委譲先 |
|---|-------|------|------|-----------|
| 1 | `/init-finance` | 基盤 | プロジェクト初期化、Zone B 自動生成 | — |
| 2 | `/data-pipeline` | データ | 市場データ取得・正規化・Parquet 保存 | data-engineer |
| 3 | `/strategy-design` | 戦略 | 並列 Researcher/Strategist 分析、Codex 設計レビュー | strategist, Codex |
| 4 | `/backtest` | 戦略 | バックテスト実行、IS/OOS 分割、Codex 統計検証 | quant-analyst, Codex |
| 5 | `/optimize` | 戦略 | Walk-forward 最適化、HPO (Optuna)、過学習検出 | quant-analyst, Codex |
| 6 | `/market-analysis` | 戦略 | マルチタイムフレーム分析、Gemini チャート認識 | Gemini |
| 7 | `/ea-generate` | EA | Python 戦略 → MQL5 EA 変換、Codex コードレビュー | ea-developer, Codex |
| 8 | `/bot-develop` | Bot | API Bot 実装（ccxt/WebSocket/async）、testnet 検証 | bot-engineer, Codex |
| 9 | `/live-trading` | Bot | 段階的ライブ移行（testnet → 最小ロット → 本番） | bot-engineer |
| 10 | `/bot-deploy` | Bot | Docker コンテナ化、systemd/launchd、ヘルスチェック | infra-ops, Codex |
| 11 | `/bot-monitor` | Bot | 構造化ログ、メトリクス、アラート閾値設定 | infra-ops |
| 12 | `/incident-response` | Bot | 緊急停止 → 根本原因分析 → 復旧 → ポストモーテム | Codex |
| 13 | `/ml-pipeline` | ML | 特徴量設計 → モデル訓練 → walk-forward (purge/embargo) → アブレーション | ml-engineer, Codex |
| 14 | `/equity-screener` | 株式 | ファンダメンタル/テクニカル スクリーニング（PER, PBR, ROE 等） | quant-analyst, Codex |
| 15 | `/earnings-calendar` | 株式 | 決算日・配当・コーポレートアクション管理 | data-engineer |
| 16 | `/sector-analysis` | 株式 | セクターパフォーマンス比較、ローテーションシグナル | quant-analyst, Codex, Gemini |
| 17 | `/ir-analysis` | 株式 | IR 資料から投資テーシス作成（財務分析 + 定性分析） | Codex, Gemini |
| 18 | `/risk-report` | リスク | VaR/CVaR、ストレステスト、相関分析 | quant-analyst, Codex |
| 19 | `/team-implement` | チーム | Agent Teams による並列実装（ファイルスコープ分離） | 全エージェント |
| 20 | `/team-review` | チーム | 3 並列レビュー（Security / Quant / Performance） | Codex |
| 21 | `/dashboard-develop` | インフラ | FastAPI + Vite SPA リアルタイムダッシュボード | infra-ops |
| 22 | `/notification-setup` | インフラ | Discord / LINE / Telegram 通知統合 | bot-engineer |
| 23 | `/codex-system` | AI直接 | Codex CLI 直接呼び出しテンプレート | Codex |
| 24 | `/gemini-system` | AI直接 | Gemini CLI 直接呼び出しテンプレート | Gemini |
| 25 | `/checkpointing` | 管理 | セッション状態スナップショット・復元 | — |

## 5. Rules（12 ルール）

`.claude/rules/` に定義されるドメインルール。全エージェントがこれらに従う。

| Rule | 適用範囲 | 主要な制約 |
|------|---------|-----------|
| `financial-domain.md` | 全体 | 数値精度は取引所仕様準拠、ルックアヘッドバイアス禁止、取引コスト (spread + commission + slippage) 必須、OOS テスト必須 (IS:OOS >= 70:30)、コーポレートアクション調整、取引時間制約 |
| `risk-management.md` | 全体 | ストップロス必須、1 トレード最大リスク 1-2%、日次損失上限 5%、多層セーフティゲート (KillSwitch, Exchange Penalty Gate, Checkpoint Gate, Maintenance Gate, Margin Monitor)、サーキットブレーカー対応、空売り規制、セクター集中制限 |
| `security.md` | 全体 | API キーは環境変数のみ、出金権限禁止、IP 制限推奨、testnet 必須、SSL/TLS 検証無効化禁止 |
| `coding-principles.md` | 全体 | 型ヒント必須、mypy strict、docstring 必須 (公開API)、テストカバレッジ 80%+、ruff、MQL5: `#property strict` |
| `testing.md` | 全体 | 戦略: backtest + unit test、データ: 統合テスト (実API)、EA: MetaTrader Tester、リスク計算: 既知値照合 |
| `language.md` | 全体 | ユーザー対話: 日本語、コード/エージェント指示: 英語、コミット: Conventional Commits |
| `bot-development.md` | Bot | ccxt 標準パターン、WebSocket 自動リコネクト、asyncio ベストプラクティス、レート制限遵守、注文状態遷移管理、Pluggable StateStore (SQLite WAL default)、取引所固有アダプターパターン、取引時間制御 |
| `deployment.md` | Bot | Docker マルチステージビルド、非 root ユーザー、ヘルスチェック必須、環境変数シークレット管理、systemd/launchd サービス、CI/CD、ロールバック手順 |
| `monitoring.md` | Bot | 構造化ログ (JSON) 必須、コアメトリクス定義 (uptime, PnL, latency, errors)、アラート閾値 (configurable)、通知チャネル (webhook)、ログローテーション |
| `document-lifecycle.md` | 全体 | 全ドキュメントの更新トリガー・責任・陳腐化検出。CLAUDE.md Zone B/C, DESIGN.md, api_specs/, reports/ の管理ポリシー。`/checkpointing` で自動チェック |
| `codex-delegation.md` | 委譲 | Codex 委譲パターン: 設計レビュー (suggest)、デバッグ (full-auto)、応答フォーマット (TL;DR → Analysis → Plan → Code → Validation → Risks) |
| `gemini-delegation.md` | 委譲 | Gemini 委譲パターン: チャート分析、PDF 解析、リサーチ。出力: 構造化 Markdown + 確信度 (High/Medium/Low) |

## 6. CLAUDE.md — 3-Zone Architecture

| Zone | 内容 | 変更方針 |
|------|------|---------|
| **A** (template-boundary 以前) | オーケストレーションルール、ルーティングポリシー、委譲トリガー、品質ゲート、言語プロトコル | 不変。テンプレートとして維持 |
| **B** (template-boundary ～ repo-boundary) | プロジェクト固有設定: 市場、データソース、実行プラットフォーム、キーコマンド | `/init-finance` で初回設定。手動編集可 |
| **C** (repo-boundary 以後) | アクティブな作業コンテキスト、設計判断ログ | セッションごとに動的更新 |

## 7. Configuration

### 7.1 External Config Files

| ファイル | 用途 | フォールバック |
|---------|------|-------------|
| `.claude/routing-keywords.json` | Hook ルーティングキーワード（エージェント別） | ビルトインデフォルト |
| `.claude/backtest-thresholds.json` | バックテスト警告閾値（メトリクス別） | ビルトインデフォルト |
| `.claude/settings.json` | Hook 登録、権限、環境変数 | — |
| `.codex/config.toml` | Codex CLI 設定 (`model = "gpt-5.4"`) | — |
| `.gemini/settings.json` | Gemini CLI 設定 (`model.name = "gemini-2.5-pro"`) | — |

### 7.2 Environment Variables

| 変数 | 設定先 |
|------|--------|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` (Agent Teams 有効化) |
| `CLAUDE_CODE_SUBAGENT_MODEL` | `claude-opus-4-6` (サブエージェントモデル) |

## 8. Prerequisites

| 要件 | バージョン | インストール |
|------|-----------|-------------|
| Claude Code | latest | `npm i -g @anthropic-ai/claude-code` |
| Codex CLI | >= 0.121.0 | `brew install codex` |
| Gemini CLI | >= 0.38.1 | `npm i -g @anthropic-ai/gemini-cli` |
| Python | >= 3.11 | [python.org](https://www.python.org/) |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

## 9. Setup

### 9.1 既存プロジェクトに導入（推奨）

既存のプロジェクトディレクトリにオーケストレーター設定を注入する:

```bash
cd /path/to/your-project
git clone --depth 1 https://github.com/ohayotaro/claude-orchestrator.git .orchestra-tmp \
  && cp -r .orchestra-tmp/.claude .orchestra-tmp/.codex .orchestra-tmp/.gemini .orchestra-tmp/CLAUDE.md . \
  && rm -rf .orchestra-tmp
claude
# Claude Code 内で:
/init-finance               # 対話形式で Zone B をプロジェクトに合わせて設定
```

コピーされるもの: `.claude/` (agents, hooks, rules, skills, settings), `.codex/`, `.gemini/`, `CLAUDE.md`

コピーされるもの: `.claude/` (agents, hooks, rules, skills, settings), `.codex/`, `.gemini/`, `CLAUDE.md`

コピーされないもの: `src/`, `mql5/`, `docker/`, `tests/`, `pyproject.toml` — これらは `/init-finance` がプロジェクトに合わせて生成する。

### 9.2 最新版に更新

導入済みプロジェクトのオーケストレーター設定を最新版に更新する。Zone B（プロジェクト固有設定）は上書きされるため、事前にバックアップすること。

```bash
cd /path/to/your-project

# 1. Zone B をバックアップ（プロジェクト固有設定を保護）
sed -n '/@orchestra:template-boundary/,/@orchestra:repo-boundary/p' CLAUDE.md > .zone-b-backup.md

# 2. カスタマイズ済み設定をバックアップ
cp .claude/routing-keywords.json .routing-keywords-backup.json 2>/dev/null
cp .claude/backtest-thresholds.json .backtest-thresholds-backup.json 2>/dev/null

# 3. 最新テンプレートで上書き
git clone --depth 1 https://github.com/ohayotaro/claude-orchestrator.git .orchestra-tmp \
  && cp -r .orchestra-tmp/.claude .orchestra-tmp/.codex .orchestra-tmp/.gemini .orchestra-tmp/CLAUDE.md . \
  && rm -rf .orchestra-tmp

# 4. バックアップを復元
mv .routing-keywords-backup.json .claude/routing-keywords.json 2>/dev/null
mv .backtest-thresholds-backup.json .claude/backtest-thresholds.json 2>/dev/null

# 5. Zone B を復元（手動: バックアップ内容を CLAUDE.md に再挿入）
# .zone-b-backup.md の内容を CLAUDE.md の @orchestra:template-boundary 以下に貼り付け
# 完了後: rm .zone-b-backup.md
```

更新されるもの: agents, hooks, rules, skills, Codex/Gemini 契約書, Zone A（テンプレートルール）

保護されるもの: `routing-keywords.json`, `backtest-thresholds.json`（バックアップ→復元）, Zone B（手動復元）, `src/`, プロジェクトコード全体

### 9.3 新規プロジェクトとして開始

スキャフォールド込みで新規プロジェクトを作成する:

```bash
git clone https://github.com/ohayotaro/claude-orchestrator.git my-trading-project
cd my-trading-project
rm -rf .git && git init     # テンプレートの git 履歴を削除
cp .env.example .env        # API キーを設定
uv sync                     # 依存関係インストール
claude
# Claude Code 内で:
/init-finance               # 対話形式でプロジェクト初期化
```

## 10. Project Structure

```
claude-orchestrator/
├── CLAUDE.md                        # 3-Zone オーケストレーター契約書
├── .claude/
│   ├── settings.json                # Hook・権限・環境変数
│   ├── agents/                      # 9 エージェント定義
│   ├── hooks/                       # 9 Python Hook
│   ├── rules/                       # 11 ドメインルール
│   ├── skills/                      # 25 スキル (SKILL.md)
│   ├── routing-keywords.json        # ルーティング設定 (customizable)
│   ├── backtest-thresholds.json     # 閾値設定 (customizable)
│   └── docs/                        # DESIGN.md, CODEX_HANDOFF_PLAYBOOK.md
├── .codex/                          # Codex CLI 契約書・設定
├── .gemini/                         # Gemini CLI 契約書・設定
├── src/
│   ├── data/                        # データ取得・管理
│   ├── strategies/                  # トレード戦略
│   ├── backtesting/                 # バックテストエンジン
│   ├── optimization/                # パラメータ最適化
│   ├── risk/                        # リスク管理
│   ├── bot/                         # API Bot エンジン
│   ├── monitoring/                  # 監視・アラート
│   └── utils/                       # ユーティリティ
├── mql5/                            # MQL5 Expert Advisors
├── docker/                          # Docker デプロイテンプレート
├── tests/                           # テストスイート
├── data/                            # データ保存 (gitignored)
├── reports/                         # レポート出力
└── pyproject.toml                   # Python 依存関係 (uv)
```

## 11. Quality Gates

オーケストレーターは応答前に以下を検証する:

1. 委譲すべきタスクを自ら処理していないか
2. 金融ドメインの正確性が確保されているか
3. リスク関連の注意事項が明記されているか
4. コンテキストウィンドウを不必要に消費していないか

バックテスト結果は以下の閾値を自動チェックする（`.claude/backtest-thresholds.json` で変更可能）:

| メトリクス | デフォルト閾値 | 判定 |
|-----------|-------------|------|
| Sharpe Ratio | < 1.0 | WARNING |
| Max Drawdown | > 20% | WARNING |
| Win Rate | < 40% | WARNING |
| Profit Factor | < 1.5 | WARNING |

## 12. References

- [claude-code-orchestra](https://github.com/DeL-TaiseiOzaki/claude-code-orchestra) — Multi-AI orchestration template
- [everything-claude-code](https://github.com/affaan-m/everything-claude-code) — Cross-harness plugin framework

## License

MIT
