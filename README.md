# Financial Trading AI Orchestrator

> **Reusable template** — clone, customize, and let the AI team build your trading system.

3つのAI（Claude, Codex, Gemini）が専門チームとして連携する、金融トレーディング開発テンプレート。暗号資産・FX・先物・株式に対応。バックテストからBot開発、デプロイ、企業分析まで、25のスキルで開発ワークフローをカバー。

---

## How It Works

Claude Code がプロジェクトマネージャーとして、タスクに応じて最適なAIに作業を委譲します。

```
┌─────────────────────────────────────────────────┐
│            Claude Code (Opus 4.6)                │
│            ── Orchestrator ──                    │
│  あなたと対話し、タスクを振り分け、結果を統合    │
├─────────────┬──────────────┬────────────────────┤
│  Subagents  │  Codex CLI   │    Gemini CLI       │
│  (Opus)     │  (GPT-5.4)   │    (Gemini 2.5 Pro) │
│             │              │                    │
│ コード探索  │ 設計・推論   │ チャート分析        │
│ レビュー    │ デバッグ     │ PDF・レポート解析   │
│ テスト作成  │ 統計検証     │ マルチモーダル      │
└─────────────┴──────────────┴────────────────────┘
```

**自動ルーティング**: 9つの Hook がプロンプト内容を分析し、最適なAI・エージェントを自動的に提案します。手動でのAI選択は不要です。

---

## Quick Start

### 前提条件

| ツール | インストール |
|--------|-------------|
| [Claude Code](https://claude.ai/code) | `npm i -g @anthropic-ai/claude-code` |
| [Codex CLI](https://github.com/openai/codex) | `brew install codex` |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | `npm i -g @anthropic-ai/gemini-cli` |
| Python 3.11+ | [python.org](https://www.python.org/) |
| [uv](https://docs.astral.sh/uv/) | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

### セットアップ

```bash
# 1. クローン
git clone https://github.com/ohayotaro/claude-orchestrator.git
cd claude-orchestrator

# 2. 環境変数の設定
cp .env.example .env
# .env を編集して取引所のAPIキーを設定

# 3. 依存関係のインストール
uv sync

# 4. Claude Code を起動
claude

# 5. プロジェクトを初期化（Claude Code 内で実行）
/init-finance
```

`/init-finance` が対話形式で市場・データソース・技術スタックを聞き取り、CLAUDE.md を自動設定します。

---

## やりたいこと別ガイド

### 戦略を開発してバックテストしたい

```
/data-pipeline          ← まずデータを取得
/strategy-design        ← 戦略を設計（Codex が統計的エッジをレビュー）
/backtest               ← バックテスト実行（Sharpe, DD, 勝率を自動計算）
/optimize               ← パラメータ最適化（過学習検出付き）
```

### 自動売買Botを開発・デプロイしたい

```
/bot-develop            ← ccxt/WebSocket ベースのBot実装
/bot-deploy             ← Docker コンテナ化 + デプロイ
/bot-monitor            ← 監視・アラート設定（Discord/Telegram等）
/live-trading           ← 段階的にライブ移行（testnet → 最小ロット → 本番）
```

### MQL5 EA を作りたい

```
/ea-generate            ← Python戦略 → MQL5 EA 変換（Codex レビュー付き）
```

### 株式を分析・スクリーニングしたい

```
/equity-screener        ← PER/PBR/ROE 等で銘柄スクリーニング
/earnings-calendar      ← 決算・配当・コーポレートアクション管理
/sector-analysis        ← セクターローテーション分析
/ir-analysis            ← IR資料から投資テーシス作成（Gemini で PDF 分析）
```

### MLモデルで予測したい

```
/ml-pipeline            ← 特徴量設計 → モデル訓練 → walk-forward 検証
```

### チャートや資料を分析したい

```
/market-analysis        ← マルチタイムフレーム分析（Gemini チャート認識）
/gemini-system          ← PDF・画像を直接 Gemini に投げる
```

### 障害が起きた

```
/incident-response      ← 緊急停止 → 根本原因分析（Codex） → ポストモーテム
```

---

## 専門チームエージェント（9名）

| エージェント | 専門領域 | いつ呼ばれるか |
|---|---|---|
| `data-engineer` | データパイプライン、API統合 | データ取得・クリーニング時 |
| `quant-analyst` | バックテスト、統計、リスク | 検証・分析時 |
| `strategist` | 戦略設計、シグナル生成 | 戦略の新規設計・改善時 |
| `ea-developer` | MQL5 EA 開発 | MetaTrader EA 作成時 |
| `bot-engineer` | API Bot、WebSocket、非同期 | Bot 実装時 |
| `infra-ops` | Docker、デプロイ、監視 | インフラ構築時 |
| `ml-engineer` | ML訓練、特徴量、検証 | 機械学習パイプライン時 |
| `codex-debugger` | エラー分析 | エラー発生時（自動検出） |
| `general-purpose` | コード探索、ドキュメント | 汎用タスク |

---

## 全25スキル一覧

<details>
<summary>クリックして展開</summary>

| カテゴリ | スキル | 説明 |
|---------|--------|------|
| **基盤** | `/init-finance` | プロジェクト初期化 |
| **データ** | `/data-pipeline` | データ取得・正規化・保存 |
| **戦略** | `/strategy-design` | 戦略設計（並列 Researcher/Strategist） |
| | `/backtest` | バックテスト実行 + Codex 統計検証 |
| | `/optimize` | パラメータ最適化（過学習検出付き） |
| | `/market-analysis` | マルチタイムフレーム + Gemini チャート分析 |
| **EA** | `/ea-generate` | Python → MQL5 EA 変換 |
| **Bot** | `/bot-develop` | API Bot 実装（ccxt, WebSocket） |
| | `/live-trading` | ライブ移行管理（段階的ロールアウト） |
| | `/bot-deploy` | Docker デプロイ + ヘルスチェック |
| | `/bot-monitor` | 監視・メトリクス・アラート |
| | `/incident-response` | 障害対応・緊急停止・ポストモーテム |
| **ML** | `/ml-pipeline` | ML モデル訓練・walk-forward 検証 |
| **株式** | `/equity-screener` | ファンダメンタル/テクニカル スクリーニング |
| | `/earnings-calendar` | 決算・配当・コーポレートアクション |
| | `/sector-analysis` | セクターローテーション分析 |
| | `/ir-analysis` | IR資料から投資テーシス作成 |
| **リスク** | `/risk-report` | VaR/CVaR, ストレステスト |
| **チーム** | `/team-implement` | Agent Teams 並列実装 |
| | `/team-review` | 3専門レビュアー並列レビュー |
| **ダッシュボード** | `/dashboard-develop` | FastAPI + Vite リアルタイム UI |
| **通知** | `/notification-setup` | Discord / LINE / Telegram 統合 |
| **AI直接** | `/codex-system` | Codex CLI 直接呼び出し |
| | `/gemini-system` | Gemini CLI 直接呼び出し |
| **保存** | `/checkpointing` | セッション状態スナップショット |

</details>

---

## カスタマイズ方法

このテンプレートを自分のプロジェクトに適用するには:

### 1. CLAUDE.md Zone B を編集

`/init-finance` が自動設定しますが、手動でも編集可能:

```markdown
@orchestra:template-boundary

## Project Identity
- **Name**: My Trading Project
- **Markets**: Crypto
- **Data Sources**: Binance API
- **Execution Platforms**: ccxt
```

### 2. ルーティングキーワードをカスタマイズ

`.claude/routing-keywords.json` を編集して、プロジェクト固有のキーワードを追加:

```json
{
  "data-engineer": ["data", "fetch", "my-custom-exchange", ...],
  "bot-engineer": ["bot", "ccxt", "my-broker-sdk", ...]
}
```

### 3. バックテスト閾値を調整

`.claude/backtest-thresholds.json` でプロジェクトに合った警告閾値を設定:

```json
{
  "sharpe": { "threshold": 1.5, "comparison": "below", ... },
  "max_drawdown": { "threshold": 15.0, "comparison": "above", ... }
}
```

---

## 裏側の仕組み

### Hook 自動ルーティング（9つ）

あなたが普通にプロンプトを入力するだけで、Hook が裏側で動きます:

- **入力時**: プロンプトを分析して最適なエージェントを提案
- **コード編集前**: 設計判断が必要な場合に Codex レビューを推奨
- **コマンド実行後**: エラーを検出したら codex-debugger を提案
- **バックテスト後**: パフォーマンス指標を自動チェック（閾値違反で警告）
- **Bot実行後**: 接続エラーや注文失敗を検出してアラート

### ルール（11個）

エージェントが従う品質基準:

- **金融ドメイン**: 数値精度、ルックアヘッドバイアス禁止、取引コスト必須
- **リスク管理**: ストップロス必須、セーフティゲート、サーキットブレーカー
- **セキュリティ**: APIキーは環境変数、testnet優先、出金権限禁止
- **コード品質**: 型ヒント、テストカバレッジ80%、ruff + mypy

### 3ゾーン CLAUDE.md

| Zone | 内容 | 変更頻度 |
|------|------|---------|
| **A** | オーケストレーションルール、委譲ポリシー | 変更しない（テンプレート） |
| **B** | プロジェクト固有設定（市場、データソース） | `/init-finance` で1回設定 |
| **C** | 作業中のコンテキスト | セッションごとに自動更新 |

---

## プロジェクト構成

```
claude-orchestrator/
├── CLAUDE.md                        # オーケストレーター契約書（3ゾーン）
├── .claude/
│   ├── settings.json                # Hook・権限設定
│   ├── agents/                      # 9 専門エージェント定義
│   ├── hooks/                       # 9 Python Hook スクリプト
│   ├── rules/                       # 11 ドメインルール
│   ├── skills/                      # 25 スキル定義
│   ├── routing-keywords.json        # ルーティングキーワード（カスタマイズ可）
│   ├── backtest-thresholds.json     # バックテスト閾値（カスタマイズ可）
│   └── docs/                        # 設計書、Codex 委譲テンプレート
├── .codex/                          # Codex CLI 設定
├── .gemini/                         # Gemini CLI 設定
├── src/                             # Python ソースコード
│   ├── data/                        #   データ取得・管理
│   ├── strategies/                  #   トレード戦略
│   ├── backtesting/                 #   バックテストエンジン
│   ├── optimization/                #   パラメータ最適化
│   ├── risk/                        #   リスク管理
│   ├── bot/                         #   API Bot エンジン
│   ├── monitoring/                  #   監視・アラート
│   └── utils/                       #   ユーティリティ
├── mql5/                            # MQL5 Expert Advisors
├── docker/                          # Docker デプロイテンプレート
├── tests/                           # テストスイート
├── data/                            # データ保存（gitignore）
├── reports/                         # レポート出力
└── pyproject.toml                   # Python 依存関係
```

---

## References

- [claude-code-orchestra](https://github.com/DeL-TaiseiOzaki/claude-code-orchestra) — Multi-AI orchestration template
- [everything-claude-code](https://github.com/affaan-m/everything-claude-code) — Cross-harness plugin framework

## License

MIT
