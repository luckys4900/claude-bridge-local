# Claude Bridge Local

Claude Code を OpenRouter / Ollama / GLM (Z.ai) で動作させるプロキシブリッジ。

## 機能

- OpenRouter API 経由で Claude Code を利用
- Ollama (ローカル LLM) のサポート
- GLM-4.7 シリーズ (Z.ai / 智谱AI) のサポート
- OpenAI 互換 API 形式への変換
- ストリーミング応答対応
- ツール呼び出し (Tool Use) 対応

## セットアップ

1. **config.json を作成**
   ```bash
   copy config.json.example config.json
   ```
2. **config.json を編集** - APIキーを設定
   - OpenRouter 使用時: `openrouter_key` を設定
   - GLM 使用時: `glm_key` または `glm_zai_key` を設定
   - Ollama 使用時: APIキー不要
3. **起動**: `start-bridge.bat` を実行

## 使い方

### 通常の起動
```bash
start-bridge.bat
```

### 環境変数で設定
```bash
# モード選択: openrouter | ollama | glm
set PROXY_MODE=openrouter

# ポート指定 (デフォルト: 9099)
set PROXY_PORT=9099

# Ollama モデル指定 (デフォルト: llama3.2:latest)
set OLLAMA_MODEL=llama3.2:latest

node proxy.mjs
```

### 各モードの詳細

#### OpenRouter モード
- 最も使いやすいクラウド API
- 複数の LLM プロバイダを利用可能
- `config.json` に `openrouter_key` を設定

#### Ollama モード
- 完全ローカルで動作
- Ollama のインストールと実行が必要
- モデルを事前にプル: `ollama pull llama3.2:latest`

#### GLM モード
- 智谱 AI (GLM-4.7 シリーズ) を利用
- `config.json` に `glm_key` を設定
- `glm_use_coding_plan: true` で Z.ai の Coding API を使用

## 必要な環境

- Node.js 18+
- (Ollama使用時) Ollama インストール済み
- (GLM使用時) 智谱 AI アカウントと API キー

## ディレクトリ構造

```
claude-bridge-local/
├── proxy.mjs                    # プロキシサーバー本体
├── config.json.example          # 設定ファイル例
├── start-bridge.bat            # 起動スクリプト (Windows)
├── Setup-GitHub-Project.ps1    # GitHub 自動セットアップ
├── backtest_ollama.mjs         # Ollama バックテスト
├── test_ollama_direct.mjs      # Ollama 直接テスト
├── README.md                   # このファイル
└── docs/                       # ドキュメント
    └── GITHUB_SETUP.md         # GitHub セットアップ手順
```

## GitHub セットアップ

このプロジェクトを GitHub に連携させるには、以下のスクリプトを実行します:

```powershell
# PowerShell で実行
.\Setup-GitHub-Project.ps1
```

または手動で設定する場合は [GITHUB_SETUP.md](GITHUB_SETUP.md) を参照。

## トラブルシューティング

### プロキシが起動しない
- Node.js がインストールされているか確認: `node --version`
- ポート 9099 が使用中でないか確認
- `config.json` の設定を確認

### Ollama に接続できない
- Ollama が実行中か確認
- `http://127.0.0.1:11434` にアクセスできるか確認

### GLM API エラー
- API キーが正しいか確認
- トークン残高を確認
- モデル名が正しいか確認 (glm-4.7, glm-4.7-flashx, etc.)

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照

## 貢献

Issue や Pull Request を歓迎します。
